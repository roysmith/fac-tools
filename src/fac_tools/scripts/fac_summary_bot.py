from argparse import ArgumentParser, BooleanOptionalAction
from collections.abc import Iterable
from datetime import datetime
from io import StringIO
import requests
from time import sleep
import urllib.parse


# from bs4 import BeautifulSoup
import humanize

# from more_itertools import flatten
import mwparserfromhell as mwp
from pywikibot import Site, Page

from fac_tools import Nomination, Revision, Index, FAToolsError

INDEX_PAGE = "Wikipedia:Featured article candidates"
SUMMARY_PAGE = "User:FACSummaryBot/summary"
REQUEST_HEADERS = {"user-agent": "fac-tools (RoySmith)"}

# Command-line args, available globally
args = None
site = None


def main():
    #
    # Note: Assumptions are made all over the place (including in how
    # the Nomination class calculates age) that the wiki is running
    # in UTC and the wiki's clock agrees with the local clock.
    #
    parser = ArgumentParser()
    parser.add_argument(
        "--dry-run",
        default=True,
        action=BooleanOptionalAction,
        help="don't write anything to the wiki, just log what would happen",
    )
    parser.add_argument("--debug", action="store_true")
    parser.add_argument(
        "--sleep",
        type=int,
        help="minutes to sleep between cycles (just runs once if ommitted)",
    )
    global args
    global site
    args = parser.parse_args()
    site = Site("en", "wikipedia")

    if args.sleep:
        while True:
            process_index()
            sleep(args.sleep * 60)
    else:
        process_index()


def process_index():
    index = Index.build(Page(site, INDEX_PAGE).text)
    buffer = StringIO()

    buffer.write(f"__NOTOC__\n")
    buffer.write(f"{{{{notice|Please don't edit this page manually!}}}}\n")

    for section_name in ["Nominations", "Older nominations"]:
        buffer.write(f"=={section_name}==\n")
        noms = index.find_noms(section_name)
        process_section(noms, buffer)

    text = buffer.getvalue()
    if args.dry_run:
        print(text)
    else:
        summary_page = Page(site, SUMMARY_PAGE)
        summary_page.text = text
        summary_page.save()


def process_section(nominations: list[Nomination], buffer: StringIO):
    now = datetime.utcnow()
    for n in nominations:
        if args.debug:
            print(n)
        nom = build_nomination(Page(site, n))
        process_nomination(nom, now, buffer)


def process_nomination(nom: Nomination, now: datetime, buffer: StringIO):
    age = nom.creation_time() - now
    active = nom.last_edit_time() - now
    article = None
    try:
        article = Page(site, nom.title())
    except FAToolsError:
        # This probably means the nomination has already been
        # promoted or archived.  We should probaby do something
        # more useful here.
        return
    description = get_short_description(article)
    url = article.full_url()
    response = requests.get(url, headers=REQUEST_HEADERS)
    response.raise_for_status()
    size = get_prose_size(article)
    rounded_size = humanize.intcomma(round(size / 100.0) * 100)

    # Isn't this why jinja templates were invented?
    buffer.write(f"<big>'''[[{nom.title()}]]'''</big>")
    buffer.write(f" ([[{nom.nomination}|nomination]]")
    if nom.archive_number() != 1:
        buffer.write(f": {humanize.ordinal(nom.archive_number())}")
    buffer.write(f")\n")
    if description:
        buffer.write(f"* ''{description}''")
    else:
        buffer.write(f"* no {{{{t|short description}}}} found")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{rounded_size} words\n")
    buffer.write(f"* {humanize.naturaldelta(age)} old")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"Active {humanize.naturaldelta(active)} ago\n")
    buffer.write(f"* {plural(len(nom.nominators()), 'nominator', 'nominators')}")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{plural(len(nom.editors()), 'participant', 'participants')}")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{plural(nom.support_count(), 'support', 'supports')}")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{plural(nom.oppose_count(), 'oppose', 'opposes')}\n")


def build_nomination(nom_page: Page) -> Nomination:
    pwb_revisions = list(nom_page.revisions(content=False))
    last_timestamp = pwb_revisions[0]["timestamp"]
    revs = list(nom_page.revisions(total=1, starttime=last_timestamp, content=True))
    text = revs[0].text
    fac_revisions = [Revision(r.timestamp, r.user) for r in pwb_revisions]
    return Nomination.build(text, nom_page.title(), fac_revisions)


def plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


def get_short_description(article: Page) -> str:
    wikicode = mwp.parse(article.text)
    templates = wikicode.filter_templates(matches="short description")
    return templates and templates[0].get(1, "")


def get_prose_size(article: Page) -> int:
    "Return the readable prose size of the page."
    site = article.site
    hostname = site.family.hostname(site.code)
    url = f"https://prosesize.toolforge.org/api/{hostname}/{urllib.parse.quote(article.title())}"
    response = requests.get(url, headers=REQUEST_HEADERS)
    response.raise_for_status()
    data = response.json()
    return data["word_count"]


if __name__ == "__main__":
    main()
