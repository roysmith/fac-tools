import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode
from textwrap import dedent

from fac_tools import Index


def test_find_noms():
    index_text = dedent(
        """\
        ==Nominations==
        {{new 1/archive1}}
        {{new 2/archive1}}

        {{new 3/archive2}}

        ==Older nominations==
        {{old 1/archive1}}
        {{old 2/archive1}}
        """
    )
    index = Index.build(index_text)
    assert list(index.find_noms("nominations")) == [
        "new 1/archive1",
        "new 2/archive1",
        "new 3/archive2",
    ]
    assert list(index.find_noms("older nominations")) == [
        "old 1/archive1",
        "old 2/archive1",
    ]
