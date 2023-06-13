r"""
Very basic script for finding duplicate cards in a deck

Change the deckname at the top
"""

deckname = 'Farnsworth -- Predator at the Chessboard'


from anki.storage import Collection
import os
import card_utils

home = os.getenv('HOME')
anki_home = home + '/Library/Application Support/Anki2/Xander'
anki_collection_path = os.path.join(anki_home, "collection.anki2")
assert os.path.exists(anki_collection_path)
col = Collection(anki_collection_path, log=True)

modelBasic = col.models.by_name('Basic')
col.decks.add_normal_deck_with_name(deckname)
deck = col.decks.by_name(deckname)
deck_id = deck.get('id')
col.decks.select(deck_id)
col.decks.current()['mid'] = modelBasic['id']

card_ids = col.decks.cids(deck_id)
card_set = set()
for cid in card_ids:
  fields = col.get_card(cid).note().fields
  assert len(fields) == 2
  front, back = fields
  clean_back = card_utils.strip_accents(back)
  board_state = card_utils.svg_str_to_board_state(front)
  cardfields = (board_state,clean_back)
  card_set.add(cardfields)


from collections import defaultdict
D = defaultdict(lambda: [])
for a,b in card_set:
  D[a].append(b)

for a in set(D.keys()):
  if len(D[a]) == 1: del D[a]
