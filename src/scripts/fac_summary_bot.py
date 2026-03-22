from argparse import ArgumentParser, BooleanOptionalAction
from collections.abc import Iterable
from io import StringIO

import humanize
import mwparserfromhell as mwp
from pywikibot import Site, Page

from fac_tools import Nomination, Revision

# Command-line args, available globally
args = None
site = None


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--dry-run",
        default=True,
        action=BooleanOptionalAction,
        help="don't write anything to the wiki, just log what would happen",
    )
    parser.add_argument("--debug", action="store_true")
    global args
    args = parser.parse_args()

    global site
    site = Site("en", "wikipedia")

    fac_index_page = Page(site, "Wikipedia:Featured article candidates")
    buffer = StringIO()

    nominations, older_nominations = find_nom_pages(fac_index_page)

    buffer.write("==Nominations==\n")
    process_section(nominations, buffer)
    buffer.write("==Older nominations==\n")
    process_section(older_nominations, buffer)

    summary_page = Page(site, "User:FACSummaryBot/summary")
    summary_page.text = buffer.getvalue()
    if args.dry_run:
        print(summary_page.text)
    else:
        summary_page.save()


def process_section(nominations: list[Nomination], buffer: StringIO):
    for n in nominations:
        if args.debug:
            print(n)
        nom = build_nomination(Page(site, n))
        process_nomination(nom, buffer)


def process_nomination(nom: Nomination, buffer: StringIO):
    buffer.write(f"* ")
    buffer.write(f"<big>[[{nom.title()}]]</big>")
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


def find_nom_pages(fac_index_page: Page) -> tuple[list[str], list[str]]:
    """Return the names of the active FAC nominations.  Two lists are
    returned: the first has the "nominations" section, the second has
    the "older nominations".
    """
    # This assumes each get_sections() call returns a single section
    code = mwp.parse(fac_index_page.text)
    for section in code.get_sections(levels=[2], matches="^nominations$"):
        nominations = list(get_nominations(section))
    for section in code.get_sections(levels=[2], matches="^older nominations$"):
        older_nominations = list(get_nominations(section))
    return nominations, older_nominations


def get_nominations(section: mwp.wikicode.Wikicode) -> Iterable[str]:
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
    return Nomination.build(text, nom_page.title(), fac_revisions)


def plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


if __name__ == "__main__":
    main()
