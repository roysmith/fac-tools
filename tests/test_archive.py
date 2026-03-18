from pathlib import Path

from mwparserfromhell.wikicode import Wikicode
import pytest

from fac_tools import Archive


@pytest.fixture
def fac(datadir: Path):
    """Return the wikitext of a FAC archive page.  The wikitext
    must already be stored in the test_archive directory.
    """

    def _fac(archive_name) -> Wikicode:
        path = datadir / "Wikipedia:Featured_article_candidates" / archive_name
        with path.open() as f:
            return f.read()

    return _fac


def test_build(fac):
    text = fac("Crusading_movement/archive2@1343969032")
    archive = Archive.build(text)
    assert isinstance(archive, Archive)
    assert isinstance(archive.wikicode, Wikicode)
    assert "===[[Crusading movement]]===" in archive.wikicode
