from argparse import ArgumentParser
from pathlib import Path

from pywikibot import Site, Page
import mwparserfromhell as mwp
import wikitextparser as wtp

FAC_LIST = "Wikipedia:List of Wikipedians by featured article nominations"


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "user",
        help="Name of user to be analyzed",
    )
    args = parser.parse_args()

    site = Site("en", "wikipedia")
    index_page = Page(site, FAC_LIST)
    code = mwp.parse(index_page.text)
    tags = code.filter_tags(recursive=False, matches="table")
    assert len(tags) == 1
    table = tags[0]
    tcode = wtp.parse(str(table))
    user = None
    for row in tcode.tables[0].data():
        for cell in row:
            if cell and "user:" in cell:
                user = cell
                continue
            if user and cell:
                print(user, cell)


if __name__ == "__main__":
    main()
