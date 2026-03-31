from __future__ import annotations
from dataclasses import dataclass
from functools import cache
import re

import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Tag, Node


@dataclass(frozen=True)
class Index:
    wikicode: Wikicode

    @staticmethod
    def build(index_page_text: str) -> Index:
        wikicode = mwp.parse(index_page_text)
        return Index(wikicode)

    def find_noms(self, section: str) -> Iterable[str]:
        """Return the names of the active FAC nominations in a given section.
        Section would typically be be one of "nominations" or "older nominations".
        It is assumed section names are unique.
        """
        sections = self.wikicode.get_sections(levels=[2], matches=f"^{section}$")
        if len(sections) != 1:
            raise ValueError(f"found {len(sections)} sections matching '{section}'")
        for t in sections[0].filter_templates(matches=".*/archive\d+"):
            yield str(t.name)
