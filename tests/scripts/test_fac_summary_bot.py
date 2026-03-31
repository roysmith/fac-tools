from pathlib import Path

from bs4 import BeautifulSoup
from more_itertools import flatten
import pytest

from fac_tools.scripts import fac_summary_bot


@pytest.mark.skip("no longer computed internally")
@pytest.mark.parametrize(
    "html,expected",
    [
        # Sizes reported by [[Wikipedia:Prosesize]]; our target
        # is +/- 15% of that.
        ("Chris Redfield@1344829095.html", 2837),
        ("Tomb of Kha and Merit@1344360978.html", 8306),
    ],
)
def test_article_size(datadir: Path, html: str, expected: int):
    path = datadir / html
    text = None
    with path.open() as f:
        text = f.read()
    word_count = fac_summary_bot.get_prose_size(text)
    assert abs(word_count - expected) <= expected * 0.15
