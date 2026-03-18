from __future__ import annotations
from dataclasses import dataclass

import mwparserfromhell as mwp


@dataclass(frozen=True)
class Archive:
    wikicode: mwp.wikicode.Wikicode

    @staticmethod
    def build(text: str) -> Archive:
        return Archive(mwp.parse(text))
