from __future__ import annotations
from dataclasses import dataclass, field

import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Tag, Node

from .revision import Revision


@dataclass(frozen=True)
class Nomination:
    wikicode: Wikicode
    revisions: list[Revision]

    @staticmethod
    def build(text: str, revisions: list[Revision] = None) -> Nomination:
        """It is assumed that revisions are in reverse chronological
        order, i.e. newest first.
        """
        wikicode = mwp.parse(text)
        if revisions:
            return Nomination(wikicode, revisions)
        else:
            return Nomination(wikicode, [])

    def _isbold(self, node: Node) -> bool:
        "Return True if node is a bit of bolded text"
        parent = self.wikicode.get_parent(node)
        return isinstance(parent, Tag) and parent.tag == "b"

    def support_count(self) -> int:
        return self._vote_count("support")

    def oppose_count(self) -> int:
        return self._vote_count("oppose")

    def _vote_count(self, word: str) -> int:
        count = 0
        for h in self.wikicode.filter_headings():
            if word.lower() in h.title.lower():
                count += 1
        for t in self.wikicode.filter_text():
            if word.lower() in t.value.lower() and self._isbold(t):
                count += 1
        return count

    def title(self) -> str:
        templates = self.wikicode.filter_templates(matches="Featured article tools")
        if len(templates) != 1:
            raise RuntimeError(
                f"There should be exactly 1 {{Featured article tools}}, found {len(templates)}"
            )
        return templates[0].get(1).value
