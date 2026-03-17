import mwparserfromhell as mwp

from fac_tools import Archive

def test_parse(datadir):
    path = datadir  / 'Wikipedia:Featured_article_candidates/Crusading_movement/archive2@1343969032'
    text = path.open().read()
    archive = Archive.build(text)
    assert isinstance(archive, Archive)
    assert isinstance(archive.wikicode, mwp.wikicode.Wikicode)