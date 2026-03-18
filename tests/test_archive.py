from pathlib import Path

from mwparserfromhell.wikicode import Wikicode
import pytest

from fac_tools import Archive


@pytest.fixture
def fac(datadir: Path):
    def _fac(archive_name: str) -> Wikicode:
        """Return the wikitext of a FAC archive page.  The wikitext
        must already be stored in the test_archive directory.

        Archive_name is the nomination page name with the leading
        'Wikipedia:Featured article candidates' stripped and '@<revision id>'
        tacked on the end, and then url-encoded.
        """
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


def test_supports(fac):
    archive = Archive.build(fac("Crusading_movement/archive2@1343969032"))
    assert archive.support_count() == 3


def test_opposes(fac):
    archive = Archive.build(
        fac("Serpent_labret_with_articulated_tongue/archive1@1343867890")
    )
    assert archive.oppose_count() == 1
