from datetime import datetime, UTC

from fac_tools import Revision


def test_construct():
    rev = Revision(datetime(2026, 1, 1, tzinfo=UTC), "RoySmith")
    assert rev.timestamp == datetime(2026, 1, 1, tzinfo=UTC)
    assert rev.username == "RoySmith"
