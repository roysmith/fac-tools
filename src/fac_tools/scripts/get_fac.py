from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dataclasses import astuple
import json
from pathlib import Path
from textwrap import dedent

from pywikibot import Site, Page
from fac_tools import Nomination, Revision


def main():
    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=dedent("""\
            Gets a WP:FAC nomination from the wiki and stores data locally.  Two
            files are created:

                - <nom>/<revid>/content.txt (the wikitext of the nonmination page)
                - <nom>/<revid>/revs.json (some data about the nomination revision history)
                                    
            These would typically be added to version control for use in unit tests.
            """),
    )
    parser.add_argument(
        "nom",
        help="Nomination page, i.e. 'Wikipedia:Featured article candidates/<nom>/archive1'",
    )
    args = parser.parse_args()

    site = Site("en", "wikipedia")
    page = Page(site, args.nom)
    revisions = list(page.revisions(content=False))
    last_timestamp = revisions[0]["timestamp"]
    last_rev = list(page.revisions(total=1, starttime=last_timestamp, content=True))[0]
    rev_id = last_rev.revid
    text = last_rev.text

    fac_revisions = [Revision(r.revid, r.user) for r in revisions]
    revision_data = [astuple(r) for r in fac_revisions]

    path = Path(page.title()) / str(rev_id)
    path.mkdir(parents=True, exist_ok=True)

    text_path = path / "content.txt"
    revs_path = path / "revs.json"

    print(text_path)
    with text_path.open("w") as f:
        f.write(text)

    print(revs_path)
    with revs_path.open("w") as f:
        json.dump(revision_data, f)


if __name__ == "__main__":
    main()
