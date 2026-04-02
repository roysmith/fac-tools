from datetime import datetime
import json
from pathlib import Path

import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode
import pytest

from fac_tools import Nomination, Revision, FAToolsError


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

        nomination_page = path.parent
        return Nomination(mwp.parse(content), nomination_page, revs)

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
    with pytest.raises(FAToolsError):
        nom.title()


def test_creation_time():
    nom = Nomination.build(
        "some random text",
        "archive",
        [
            Revision(datetime(2026, 3, 3), "user3"),
            Revision(datetime(2026, 3, 2), "user2"),
            Revision(datetime(2026, 3, 1), "user1"),
        ],
    )
    assert nom.creation_time() == datetime(2026, 3, 1)


def test_creation_time_raises_with_no_revisions():
    nom = Nomination.build("some random text", "archive", [])
    with pytest.raises(ValueError):
        nom.creation_time()


def test_last_edit_time():
    nom = Nomination.build(
        "some random text",
        "archive",
        [
            Revision(datetime(2026, 3, 3), "user3"),
            Revision(datetime(2026, 3, 2), "user2"),
            Revision(datetime(2026, 3, 1), "user1"),
        ],
    )
    assert nom.last_edit_time() == datetime(2026, 3, 3)


def test_last_edit_time_raises_with_no_revisions():
    nom = Nomination.build("some random text", "archive", [])
    with pytest.raises(ValueError):
        nom.last_edit_time()


def test_nominators_with_one(fac):
    nom = fac("Crusading movement/archive2/1344125955")
    assert nom.nominators() == ["Borsoka"]


def test_nominators_with_two(fac):
    nom = fac("Horizon Zero Dawn/archive1/1344093782")
    assert nom.nominators() == ["ZooBlazer", "OceanHok"]


def test_nominators_raises_with_no_data():
    nom = Nomination.build("Nothing to see here", "archive", [])
    with pytest.raises(ValueError, match="can't find nominators element"):
        nom.nominators()


def test_editors():
    nom = Nomination.build(
        "blah",
        "archive",
        [
            Revision(datetime(2026, 1, 1), "user1"),
            Revision(datetime(2026, 1, 1), "user1"),
            Revision(datetime(2026, 1, 1), "user2"),
            Revision(datetime(2026, 1, 1), "user1"),
            Revision(datetime(2026, 1, 1), "user3"),
            Revision(datetime(2026, 1, 1), "user4"),
        ],
    )
    assert nom.editors() == {"user1", "user2", "user3", "user4"}


def test_archive_number(fac):
    cm = fac("Crusading movement/archive2/1344125955")
    hzd = fac("Horizon Zero Dawn/archive1/1344093782")
    assert cm.archive_number() == 2
    assert hzd.archive_number() == 1


def test_archive_number_raises_on_malformed_nomination():
    nom = Nomination.build(
        "whatever", "Wikipedia:Featured article candidates/Nile/archive", []
    )
    with pytest.raises(ValueError, match="malformed nomination path"):
        nom.archive_number()


@pytest.mark.xfail(
    reason="https://github.com/earwig/mwparserfromhell/issues/353",
    strict=True,
)
def test_unbolded_oppose_does_not_count_as_vote(fac):
    nom = fac("Nile/archive1/1346716243")
    assert nom.oppose_count() == 1
