from fac_tools import Nomination, Revision
from pywikibot import Site, Page


def main():
    site = Site("en", "wikipedia")
    page = Page(
        site, "Wikipedia:Featured article candidates/Crusading movement/archive2"
    )
    nomination = build_nomination(page)
    print(nomination)


def build_nomination(page: Page) -> Nomination:
    ft_revs = []
    for pwb_rev in page.revisions():
        ft_revs.append(Revision(pwb_rev.timestamp, pwb_rev.user))
    return Nomination.build(page.get(), ft_revs)


if __name__ == "__main__":
    main()
