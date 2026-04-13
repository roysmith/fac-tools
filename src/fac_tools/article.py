from __future__ import annotations
from dataclasses import dataclass
from sys import argv

import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode
import requests


@dataclass(frozen=True)
class Article:
    wikicode: Wikicode
    parsoid_html: str

    @staticmethod
    def build(text: str, parsoid_html: str) -> Article:
        wikicode = mwp.parse(text)
        return Article(wikicode, parsoid_html)

    def short_description(self) -> str:
        """Return the text of the {{short description}}.  If no
        such template exists, return something falsy.
        """
        templates = self.wikicode.filter_templates(matches="short description")
        return templates and templates[0].get(1, "")

    def prose_size(self) -> int:
        "Return the readable prose size in words."
        url = "https://prosesize.toolforge.org/api/html"
        headers = {
            "user-agent": f"fac_tools ({argv[0]})",
            "content-type": "test/html",
        }
        r = requests.post(url, headers=headers, data=self.parsoid_html)
        r.raise_for_status()
        data = r.json()
        return data["word_count"]
