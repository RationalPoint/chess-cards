#!/usr/local/bin/python

r"""Script to make flash cards out of a collection of fens and strings describing
solutions to the problems.

The file that holds the position data should be a yaml file corresponding to a
dictionary whose keys are cards (named whatever, the card names aren't used),
and whose values are dicts with the following key/value pairs:

  'fen': a fen string for the position
  'description': Description of the card (type of puzzle, 
                 where in the book it's from, etc.)
  'instructions': Instructions for the puzzle (if not given, 
                  White/Black to move will be used)
  'solution': The solution to the puzzle.

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


TODO:
- Is there an attribute to organize decks together? This seemed possible when I
  looked at shared decks.
- Do I want to add some html for lists when I have multiple variations like (A), (B), (C), etc.?

"""

import argparse
import os
import re
import subprocess
import sys
import yaml

from anki.storage import Collection 
import chess, chess.svg

################################################################################
#################################  UTILITIES  ##################################
################################################################################

def fen_to_svg_str(fen, numpixels=None, coordinates=False, colors=None):
  r"""
  Convert a fen into an svg string

  INPUT:

  - ``fen`` -- a well-formed fen string

  - ``numpixels`` -- optional number of pixels for the height/width of the board

  - ``coordinates`` -- bools (default: False); whether to print coordinates
    around the board

  - ``colors`` -- optional pair of HTML color strings to determine the light and
    dark color squares on the board (default: ('ffce9e','d18b47'))

  OUTPUT:

  - A string representation of the svg needed to reproduce this board in a web browser

  """
  b = chess.Board(fen)
  s = chess.svg.board(b,coordinates=coordinates)
  if numpixels is not None:
    if s[:5] != '<svg ':
      raise RuntimeError('Unable to set number of pixels for this svg')
    tmp = '<svg '
    tmp += 'width="{}" height="{}" '.format(numpixels,numpixels)
    tmp += s[5:]
    s = tmp

  if colors is None:
    return s

  light,dark = colors
  s = s.replace('ffce9e',light)
  s = s.replace('d18b47',dark)
  return s

def write_fen_to_svg(fen, fileprefix, numpixels=None, coordinates=False, colors=None):
  s = fen_to_svg_str(fen,numpixels,coordinates,colors=colors)
  fp = open(fileprefix+'.svg','w')
  fp.write(s)
  fp.close()

def write_fen_to_png(fen, fileprefix, numpixels=None, coordinates=False, colors=None):
  write_fen_to_svg(fen,fileprefix,coordinates=coordinates,colors=colors)
  cmd = ['qlmanage','-t','-s',str(numpixels),'-o','.',fileprefix+'.svg']
  subprocess.run(cmd,stderr=subprocess.DEVNULL,stdout=subprocess.DEVNULL)
  cmd = ['rm', fileprefix + '.svg']
  subprocess.run(cmd)
  return

def convert_ordered_list_to_html(string):
  r"""
  Parse a string with "(A) ... (B) ... etc." and write in html format

  NOTE:

  - We assume that if there is an ordered list, it is indexed by
    single-character identifiers like A, B, C, etc. Also, if there
    are fewer than 2 list items, no changes are made. 

  """
  matches = re.findall('\((\w)\)',s)
  if len(matches) < 2:
    return string
  new_string = ''
  for c in matches:
    tmp = string.split('({}')
  # <ol type="A">'
  

################################################################################

# Color schemes
color_schemes = {}
color_schemes['blue']   = ('eeeed2','6188b5')
color_schemes['brown']  = ('f0d9b5','b58863')
color_schemes['gray']   = ('c8c8c8','939393')
color_schemes['green']  = ('eeeed2','769656')
color_schemes['pink']   = ('eeeed2','f27372')
color_schemes['purple'] = ('eeeed2','c0a2c7')

################################################################################

# Parse arguments

msg = "Script for converting chess fen's and text into Anki flash cards"
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

colorchoice = args.colorscheme
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
    s += '  solution:\n\n'
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

# Set up the deck model
modelBasic = col.models.by_name('Basic')
col.decks.add_normal_deck_with_name(deckname)
deck = col.decks.by_name(deckname)
deck_id = deck['id']
col.decks.select(deck_id)
col.decks.current()['mid'] = modelBasic['id']

# Make one pass through the existing cards in the deck to avoid creaing
# duplicates. This is useful when making cards before all position have been
# transcribed and solved.
card_ids = col.decks.cids(deck_id)
card_set = set()
for cid in card_ids:
  fields = col.get_card(cid).note().fields
  cardstr = ''.join(fields)
  card_set.add(cardstr)

colors = color_choice()
puzzle_dict = yaml.safe_load(open(fenfile,'r'))
num_puzzles = len([key for key,val in puzzle_dict.items() if val['fen'] is not None])
print('Looking at {} cards ... '.format(num_puzzles),end='')
cnt = 0
for card in puzzle_dict.values():
  fen   = card.get('fen')
  instr = card.get('instructions')
  desc  = card.get('description','')
  soln  = card.get('solution')
  if fen is None or soln is None:
    continue

  if instr is None:
    to_move = 'White' if chess.Board(fen).turn else 'Black'
    instr = to_move + ' to move'
    
  pos = fen_to_svg_str(fen,numpixels,colors=next(colors))

  front = pos + r'<br><hr3><i>' + instr + r'</i></hr3>'

  
  back = r'<b>' + soln + r'</b>'
  if desc is not None:
    back += r'<hr>' + desc
    
  if front + back in card_set:
    # We have already created this card!
    continue

  # Create a new card: custom format done already in Anki
  note = col.newNote()
  note.fields[0] = front
  note.fields[1] = back
  note.tags = [''.join(desc.split())] # String without spaces as tag
  col.add_note(note, deck_id)
  cnt += 1

print('created {} cards!'.format(cnt))
col.save()  
sys.exit(0)  
