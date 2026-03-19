from __future__ import annotations
from dataclasses import dataclass

import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Tag, Node


@dataclass(frozen=True)
class Nomination:
    wikicode: Wikicode

    @staticmethod
    def build(text: str) -> Nomination:
        return Nomination(mwp.parse(text))

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
