from datetime import datetime, timedelta, UTC
import json
from pathlib import Path
from unittest.mock import patch

from mwparserfromhell.wikicode import Wikicode
import pytest

from fac_tools import Nomination, Revision


@pytest.fixture
def fac(datadir: Path):
    def _fac(nomination_name: str) -> Nomination:
        """Return a Nomination from the stored data in the test_nomination directory.

        Nomination_name is the nomination page name with the leading
        'Wikipedia:Featured article candidates' stripped and '/<revision id>'
        tacked on the end.  It is assumed that the part before the '/<revision id>'
        is 'archive<N>'.
        """
        path = datadir / "Wikipedia:Featured article candidates" / nomination_name
        content = None
        with (path / "content.txt").open() as f:
            content = f.read()

        data = None
        with (path / "revs.json").open() as f:
            data = json.load(f)
        revs = [Revision(*d) for d in data]

        nomination_page = path.parent()
        return Nomination(content, nomination_page, revs)

    return _fac


def test_build_with_no_revisions():
    nom = Nomination.build("blah", "archive99", [])
    assert isinstance(nom, Nomination)
    assert isinstance(nom.wikicode, Wikicode)
    assert nom.wikicode == "blah"
    assert nom.nomination == "archive99"
    assert nom.revisions == []


def test_supports(fac):
    nom = fac("Crusading movement/archive2/1344125955")
    assert nom.support_count() == 3


def test_opposes(fac):
    nom = fac("Serpent labret with articulated tongue/archive1/1344457733")
    assert nom.oppose_count() == 1


def test_title(fac):
    nom = fac("Crusading movement/archive2/1344125955")
    assert nom.title() == "Crusading movement"


def test_title_raises_with_missing_template():
    nom = Nomination.build("I am broken", "archive", [])
    with pytest.raises(RuntimeError):
        nom.title()


@patch("fac_tools.nomination.datetime")
def test_age(mock_datetime):
    mock_datetime.now.return_value = datetime(2026, 3, 10, tzinfo=UTC)
    nom = Nomination.build(
        "some random text",
        "archive",
        [
            Revision(datetime(2026, 3, 3, tzinfo=UTC), "user3"),
            Revision(datetime(2026, 3, 2, tzinfo=UTC), "user2"),
            Revision(datetime(2026, 3, 1, tzinfo=UTC), "user1"),
        ],
    )
    assert nom.age() == timedelta(days=9)


def test_age_raises_with_no_revisions():
    nom = Nomination.build("some random text", "archive", [])
    with pytest.raises(ValueError):
        nom.age()


@patch("fac_tools.nomination.datetime")
def test_active(mock_datetime):
    mock_datetime.now.return_value = datetime(2026, 3, 10, tzinfo=UTC)
    nom = Nomination.build(
        "some random text",
        "archive",
        [
            Revision(datetime(2026, 3, 3, tzinfo=UTC), "user3"),
            Revision(datetime(2026, 3, 2, tzinfo=UTC), "user2"),
            Revision(datetime(2026, 3, 1, tzinfo=UTC), "user1"),
        ],
    )
    assert nom.active() == timedelta(days=7)


def test_active_raises_with_no_revisions():
    nom = Nomination.build("some random text", "archive", [])
    with pytest.raises(ValueError):
        nom.active()


def test_nominators_with_one(fac):
    nom = fac("Crusading movement/archive2/1344125955")
    assert nom.nominators() == ["Borsoka"]


def test_nominators_with_two(fac):
    nom = ac("Horizon Zero Dawn/archive1/1344093782")
    assert nom.nominators() == ["ZooBlazer", "OceanHok"]


def test_nominators_raises_with_no_data():
    nom = Nomination.build("Nothing to see here", "archive", [])
    with pytest.raises(ValueError, match="can't find nominators element"):
        nom.nominators()
