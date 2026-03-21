from argparse import ArgumentParser, BooleanOptionalAction
from collections.abc import Iterable
from io import StringIO

import humanize
import mwparserfromhell as mwp
from pywikibot import Site, Page

from fac_tools import Nomination, Revision


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--dry-run",
        default=True,
        action=BooleanOptionalAction,
        help="don't write anything to the wiki, just log what would happen",
    )
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    site = Site("en", "wikipedia")

    fac_index_page = Page(site, "Wikipedia:Featured article candidates")
    buffer = StringIO()

    for n in find_nom_pages(fac_index_page):
        if args.debug:
            print(n)
        nom = build_nomination(Page(site, n))
        process_nomination(nom, buffer)

    summary_page = Page(site, "User:FACSummaryBot/summary")
    summary_page.text = buffer.getvalue()
    if args.dry_run:
        print(summary_page.text)
    else:
        summary_page.save()


def process_nomination(nom: Nomination, buffer: StringIO):
    buffer.write(f"* ")
    buffer.write(f"[[{nom.title()}]]")
    buffer.write(f" (")
    buffer.write(f"[[{nom.nomination}|nomination]]")
    if nom.archive_number() != 1:
        buffer.write(f": {humanize.ordinal(nom.archive_number())}")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{humanize.naturaldelta(nom.age())} old")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"Active {humanize.naturaldelta(nom.active())} ago")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{plural(len(nom.nominators()), 'nominator', 'nominators')}")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{plural(len(nom.editors()), 'participant', 'participants')}")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{plural(nom.support_count(), 'support', 'supports')}")
    buffer.write(f"{{{{cdot}}}}")
    buffer.write(f"{plural(nom.oppose_count(), 'oppose', 'opposes')}")
    buffer.write(f")\n")


def find_nom_pages(fac_index_page: Page) -> Iterable[str]:
    "Return the names of the active FAC nominations"
    code = mwp.parse(fac_index_page.text)
    for section in code.get_sections(levels=[2], matches="nominations"):
        for t in section.filter_templates(
            matches="Wikipedia:Featured article candidates/.*/archive\d+"
        ):
            yield str(t.name)


def build_nomination(nom_page: Page) -> Nomination:
    pwb_revisions = list(nom_page.revisions(content=False))
    last_timestamp = pwb_revisions[0]["timestamp"]
    revs = list(nom_page.revisions(total=1, starttime=last_timestamp, content=True))
    text = revs[0].text
    fac_revisions = [Revision(r.timestamp, r.user) for r in pwb_revisions]
    return Nomination(mwp.parse(text), nom_page.title(), fac_revisions)


def plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


if __name__ == "__main__":
    main()
