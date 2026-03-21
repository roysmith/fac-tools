from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import mwparserfromhell as mwp
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes import Tag, Node

from .revision import Revision


@dataclass(frozen=True)
class Nomination:
    wikicode: Wikicode
    nomination: str  # 'Wikipedia:Featured article candidates/Foo/archiveN'
    revisions: list[Revision]

    @staticmethod
    def build(text: str, nomination: str, revisions: list[Revision]) -> Nomination:
        """It is assumed that revisions are in reverse chronological
        order, i.e. newest first.
        """
        wikicode = mwp.parse(text)
        return Nomination(wikicode, nomination, revisions)

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

    def age(self) -> timedelta:
        """Return the age of this nomination.  Assuming the oldest revision
        is in the past, this will be positive.
        """
        if self.revisions:
            oldest_timestamp = self.revisions[-1].timestamp
            now = datetime.utcnow()
            return now - oldest_timestamp
        else:
            raise ValueError("nomination has no revisions")

    def active(self) -> timedelta:
        """Return the time since this nomination was last edited.  Assuming
        the newest revision is in the past, this will be positive.
        """
        if self.revisions:
            newest_timestamp = self.revisions[0].timestamp
            now = datetime.utcnow()
            return now - newest_timestamp
        else:
            raise ValueError("nomination has no revisions")

    def nominators(self) -> list[str]:
        """Returns a list of the nominators's usernames"""
        for tag in self.wikicode.filter_tags(matches="small"):
            if tag.contents.startswith("Nominator(s):"):
                nominators = []
                for link in tag.contents.filter_wikilinks():
                    if link.title.startswith("User:"):
                        nominators.append(link.title.removeprefix("User:"))
                return nominators
        raise ValueError("can't find nominators element")

    def editors(self) -> set(str):
        "Returns the usernames of all the editors of this nomination"
        return set(rev.username for rev in self.revisions)
