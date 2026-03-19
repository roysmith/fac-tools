from pathlib import Path

from mwparserfromhell.wikicode import Wikicode
import pytest

from fac_tools import Nomination


@pytest.fixture
def fac(datadir: Path):
    def _fac(nomination_name: str) -> str:
        """Return the wikitext of a FAC nomination page.  The wikitext
        must already be stored in the test_nomination directory.

        Nomination_name is the nomination page name with the leading
        'Wikipedia:Featured article candidates' stripped and '@<revision id>'
        tacked on the end, and then url-encoded.
        """
        path = datadir / "Wikipedia:Featured_article_candidates" / nomination_name
        with path.open() as f:
            return f.read()

    return _fac


def test_build_with_no_revisions(fac):
    text = fac("Crusading_movement/archive2@1343969032")
    nom = Nomination.build(text)
    assert isinstance(nom, Nomination)
    assert isinstance(nom.wikicode, Wikicode)
    assert "===[[Crusading movement]]===" in nom.wikicode
    assert nom.revisions == []


def test_supports(fac):
    nom = Nomination.build(fac("Crusading_movement/archive2@1343969032"))
    assert nom.support_count() == 3


def test_opposes(fac):
    nom = Nomination.build(
        fac("Serpent_labret_with_articulated_tongue/archive1@1343867890")
    )
    assert nom.oppose_count() == 1


def test_title(fac):
    nom = Nomination.build(fac("Crusading_movement/archive2@1343969032"))
    assert nom.title() == "Crusading movement"


def test_title_throws_with_missing_template():
    nom = Nomination.build("I am broken")
    with pytest.raises(RuntimeError):
        nom.title()
