import pytest
from pytest_socket import SocketBlockedError

from fac_tools import Article


def test_missing_short_description():
    article = Article.build("foo", "<p>foo</p>")
    assert not article.short_description()


@pytest.mark.xfail(
    reason="socket intentionally blocked in conftest.py",
    raises=SocketBlockedError,
    strict=True,
)
def test_prose_size():
    article = Article.build("foo", "<p>foo</p>")
    assert article.prose_size() > 0
