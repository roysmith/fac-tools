from collections.abc import Iterable

import humanize
import mwparserfromhell as mwp
from pywikibot import Site, Page

from fac_tools import Nomination, Revision


def main():
    site = Site("en", "wikipedia")

    fac_index_page = Page(site, "Wikipedia:Featured article candidates")
    for n in find_nom_pages(fac_index_page):
        nom = build_nomination(Page(site, n))
        process_nomination(nom)


def process_nomination(nom: Nomination):
    print(
        f"* "
        f"[[{nom.title()}]]"
        f" ("
        f"[[{nom.nomination}|nomination]]"
        f": {humanize.ordinal(nom.archive_number())}"
        f"{{{{cdot}}}}"
        f"{humanize.naturaldelta(nom.age())} ago"
        f"{{{{cdot}}}}"
        f"Active {humanize.naturaldelta(nom.active())} ago"
        f"{{{{cdot}}}}"
        f"{plural(len(nom.nominators()), 'nominator', 'nominators')}"
        f"{{{{cdot}}}}"
        f"{plural(len(nom.editors()), 'participant', 'participants')}"
        f"{{{{cdot}}}}"
        f"{plural(nom.support_count(), 'support', 'supports')}"
        f"{{{{cdot}}}}"
        f"{plural(nom.oppose_count(), 'oppose', 'opposes')}"
        f")"
    )


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
