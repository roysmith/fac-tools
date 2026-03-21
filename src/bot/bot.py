from humanize import naturaltime, naturaldelta

import mwparserfromhell as mwp
from pywikibot import Site, Page

from fac_tools import Nomination, Revision


def main():
    site = Site("en", "wikipedia")
    nomination_page = (
        "Wikipedia:Featured article candidates/Crusading movement/archive2"
    )
    page = Page(site, nomination_page)

    pwb_revisions = list(page.revisions(content=False))
    last_timestamp = pwb_revisions[0]["timestamp"]
    last_rev = list(page.revisions(total=1, starttime=last_timestamp, content=True))[0]
    text = last_rev.text
    fac_revisions = [Revision(r.timestamp, r.user) for r in pwb_revisions]

    nom = Nomination(mwp.parse(text), nomination_page, fac_revisions)
    print(
        f"[[{nom.title()}]]"
        f" ("
        f"[[{nom.nomination}|nomination]]{{{{cdot}}}}"
        f"{naturaldelta(nom.age())} ago{{{{cdot}}}}"
        f"Active {naturaldelta(nom.active())} ago{{{{cdot}}}}"
        f"{plural(len(nom.nominators()), 'nominator', 'nominators')}{{{{cdot}}}}"
        f"{plural(len(nom.editors()), 'participant', 'participants')}{{{{cdot}}}}"
        f"{plural(nom.support_count(), 'support', 'supports')}{{{{cdot}}}}"
        f"{plural(nom.oppose_count(), 'oppose', 'opposes')}"
        f")"
    )


def plural(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


# def build_nomination(page: Page) -> Nomination:
#     fac_revs = []
#     for pwb_rev in page.revisions():
#         fac_revs.append(Revision(pwb_rev.timestamp, pwb_rev.user))
#     return Nomination.build(page.get(), fac_revs)


if __name__ == "__main__":
    main()
