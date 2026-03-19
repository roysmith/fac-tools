from datetime import datetime, timezone


from fac_tools import Revision


def test_construct():
    rev = Revision(datetime(2026, 1, 1, tzinfo=timezone.utc), "RoySmith")
    assert rev.timestamp == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert rev.username == "RoySmith"
