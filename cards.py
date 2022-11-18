#!/usr/local/bin/python

"""Script to make flash cards out of a collection of fens and strings describing
solutions to the problems.

The file that holds the position data should be a yaml file corresponding to a
dictionary whose keys are cards (named whatever, the card names aren't used), and whose values are dicts with the following key/value pairs:

  'fen': a fen string for the position (required)
  'description': Description of the card, type of puzzle, 
                 where in the book it's from, etc. (optional)
  'instructions': Instructions for the puzzle (optional; if not given, 
                  "White/Black to move" will be used)
  'solution': The solution to the puzzle (required)
  'difficulty': easy/hard (optional; if not given, "easy" is assumed)

Top color choices (light/black squares):
  chess.com colors: eeeed2/769656
  pale blue: eeeed2/6188b5
  purple: eeeed2/c0a2c7
  lichess colors: f0d9b5/b58863
  newspaper colors: c8c8c8/939393
  pink: eeeed2/f27372

To avoid the possibility of wrecking my main Anki collection, I develop new
decks in a sandboxed environment /Library/Anki. Once that's working, I export
the deck and then import it to my main Anki environment (the one that's sync'd
across devices).

Note: There is a weird bug in chess.svg.board that sometimes renders the svg
string with <path .../></path> and sometimes renders it with <path .../>. This
disrupts the ability to determine when two puzzles are the same, so I strip out
the board state rather than compare the whole string.

Note: There is another odd behavior I found where Anki stores the raw html when
I access it through python, but it converts the raw html into unicode when I
open the gui. This presented by creating duplicate cards if the card info
contained an html accent like '&eacute;'. Now I strip the accents when
comparing the existing cards with potential new cards.

"""

import argparse
import os
import subprocess
import sys
import yaml


from anki.storage import Collection 
import card_utils
import chess


################################################################################

# Parse arguments

msg = "Script for converting chess fens and text into Anki flash cards"
parser = argparse.ArgumentParser(description=msg)

kwargs = {}
kwargs['type']=str
kwargs['help'] = 'File containing fens and text'
parser.add_argument('fen_file',**kwargs)

kwargs = {}
kwargs['action'] = 'store_true'
kwargs['help'] = 'Write to the real Anki collection, not the sandbox.'
parser.add_argument('-r','--realthing',**kwargs)

kwargs = {}
kwargs['type'] = int
kwargs['help'] = 'Number of pixels for height/width of boards'
kwargs['default'] = 380 # Fits well on phone/tablet/computer
parser.add_argument('-n','--numpixels',**kwargs)

kwargs = {}
kwargs['type'] = str
kwargs['help'] = 'Name of deck to use when writing cards (default: prefix of fen_file)'
parser.add_argument('-d','--deckname',**kwargs)

kwargs = {}
kwargs['type'] = str
kwargs['help'] = 'Name of color scheme to use'
kwargs['choices'] = ['blue','brown','gray','green','pink','purple','all']
kwargs['default'] = 'all'
parser.add_argument('-c','--colorscheme',**kwargs)

kwargs = {}
kwargs['type'] = int
kwargs['help'] = 'Make a template yaml file with this many cards and write to "fen_file".'
kwargs['default'] = 0
parser.add_argument('-t','--template',**kwargs)

args = parser.parse_args()

fenfile = args.fen_file

numpixels = args.numpixels

deckname = args.deckname
if deckname is None:
  # Get deck name: assuming fenfile of the form blah/blah/blah/blah.fen
  filename = fenfile.split('/')[-1]
  deckname,_ = filename.split('.')
decknames = [deckname] # If appropriate, add deckname for hard puzzles later

colorchoice = args.colorscheme
color_schemes = card_utils.color_schemes
if colorchoice == 'all':
  scriptcolors = list(color_schemes.values())
else:
  assert colorchoice in color_schemes
  scriptcolors = [color_schemes[colorchoice]]
  
def color_choice():
  i = 0
  n = len(scriptcolors)
  while True:
    yield scriptcolors[i%n]
    i += 1

home = os.getenv('HOME')
if args.realthing:
  anki_home = home + '/Library/Application Support/Anki2/Xander'
else:
  anki_home = home + '/Library/Anki/Xander'

################################################################################

# Do we make a template file?
if args.template > 0:
  if os.path.exists(fenfile):
    print('File {} already exists; cannot overwrite with a template.'.format(fenfile))
    sys.exit(1)
  s = ''
  for n in range(1,args.template+1):
    s += 'card{}:\n'.format(n)
    s += '  description: "Position :"\n'
    s += '  fen:\n'
    s += '  instructions:\n'
    s += '  solution:\n'
    s += '  difficulty:\n'
    s += '  tag:\n\n'
  fp = open(fenfile,'w')
  fp.write(s)
  fp.close()
  sys.exit(0)

################################################################################

# Now we are making an anki collection. 
if not os.path.exists(fenfile):
  print('File {} does not exist; no fens available'.format(fenfile))
  sys.exit(1)

# Find/Load the Anki directory 
anki_collection_path = os.path.join(anki_home, "collection.anki2")
assert os.path.exists(anki_collection_path)
col = Collection(anki_collection_path, log=True)

# Run through cards in yaml file and create puzzles dict:
#   keys are 'easy' and 'hard', values are dicts with keys {deckname, puzzles}
puzzle_dict = yaml.safe_load(open(fenfile,'r'))
allpuzzles = {} 
num_puzzles = 0
print('Scanning {} puzzle stubs'.format(len(puzzle_dict)))
soln_with_no_fen = 0
fen_with_no_soln = 0
for key,val in puzzle_dict.items():
  fen = val.get('fen')
  soln = val.get('solution')
  desc = val.get('description')
  diff = val.get('difficulty')
  tag = val.get('tag')
  if soln is not None and fen is None:
    soln_with_no_fen += 1
    continue
  if fen is not None and soln is None:
    fen_with_no_soln += 1
    continue
  if fen is None or soln is None:
    # print('fen',key)
    # print('solution',key)
    continue
  if tag is None:
    print('WARNING: No tag for {}'.format(desc))
    continue
  if diff is None:
    diff = 'easy'
  else:
    diff = diff.strip().lower()
  if diff not in ['easy','hard']:
    raise ValueError('Expected difficulty to be easy/hard, got {}'.format(diff))
  num_puzzles += 1
  if diff in allpuzzles:
    D = allpuzzles[diff]
  else:
    allpuzzles[diff] = D = {}
    if diff == 'easy':
      D['deckname'] = deckname
    else:
      D['deckname'] = 'Hard: ' + deckname
    D['puzzles'] = []
  D['puzzles'].append(val)
if soln_with_no_fen > 0:
  print('  ==> {} puzzle stubs with a solution and no fen'.format(soln_with_no_fen))
if fen_with_no_soln > 0:
  print('  ==> {} puzzle stubs with a fen and no solution'.format(fen_with_no_soln))

print('  ==> {} complete puzzles'.format(num_puzzles))  

for puzztype, D in allpuzzles.items():
  deckname = D.get('deckname')
  puzzles = D.get('puzzles')
  
  # Set up the deck model
  modelBasic = col.models.by_name('Basic')
  col.decks.add_normal_deck_with_name(deckname)
  deck = col.decks.by_name(deckname)
  deck_id = deck.get('id')
  col.decks.select(deck_id)
  col.decks.current()['mid'] = modelBasic['id']

  # Make one pass through the existing cards in the deck to avoid creaing
  # duplicates. This is useful when making cards before all positions have been
  # transcribed and solved.
  card_ids = col.decks.cids(deck_id)
  card_set = set()
  for cid in card_ids:
    fields = col.get_card(cid).note().fields
    assert len(fields) == 2
    front, back = fields
    board_state = card_utils.svg_str_to_board_state(front)
    clean_back = card_utils.strip_accents(back) # avoid unicode/html accent conversion
    cardfields = (board_state,clean_back)
    card_set.add(cardfields)

  colors = color_choice()
  cnt = 0
  for card in puzzles:
    fen   = card.get('fen')
    instr = card.get('instructions')
    desc  = card.get('description')
    soln  = card.get('solution')
    tag   = card.get('tag')
    assert fen is not None  # Already filtered for this
    assert soln is not None # Already filtered for this
    
    if instr is None:
      to_move = 'White' if chess.Board(fen).turn else 'Black'
      instr = to_move + ' to move'

    pos = card_utils.fen_to_svg_str(fen,numpixels,colors=next(colors))

    front = pos + r'<br><hr3><i>' + instr + r'</i></hr3>'

    soln = card_utils.convert_ordered_list_to_html(soln) # parse HTML lists
    back = r'<b>' + soln + r'</b>'
    if desc is not None:
      back += r'<hr>' + desc

    board_state = card_utils.svg_str_to_board_state(pos)
    clean_back = card_utils.strip_accents(back) # avoid unicode/html accent conversion
    if (board_state,clean_back) in card_set:
      # We have already created this card!
      continue

    # Create a new card: custom format done already in Anki
    note = col.newNote()
    note.fields[0] = front
    note.fields[1] = back
    note.tags = tag.split()
    col.add_note(note, deck_id)
    cnt += 1

  s = '' if cnt == 1 else 's'
  print('  ==> created {} {} card{}'.format(cnt,puzztype,s))
  col.save()
  
sys.exit(0)  
