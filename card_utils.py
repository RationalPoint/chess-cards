
import chess, chess.svg
import re

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

def svg_str_to_board_state(string):
  """Grab the board state from an svg string"""
  L = string.split('pre')
  msg = 'Expected to find "pre" twice in string, got {}'
  if len(L) != 3:
    raise RuntimeError(msg.format(len(L)-1))
  return L[1][1:-2]

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
  matches = re.findall('\((\w)\)',string) # Grab letters A,B,C in parens
  if len(matches) < 2:
    return string
  if matches[0] != 'A':
    raise RuntimeError('Expected (A) for first list item, got {}'.format(matches[0]))
  
  new_string = ''
  numitems = len(matches)
  for i,c in enumerate(matches):
    tmp = string.split('({})'.format(c))
    if len(tmp) != 2:
      msg = 'Unable to split the following string at ({}):\n  {}'
      raise RuntimeError(msg.format(c,string))
    new_string += tmp[0]
    string = tmp[1]
    if i == 0:
      new_string += '<ol type="A"><li>'
    elif i < numitems-1:
      new_string += '</li><li>'
    else:
      new_string += '</li><li>' + tmp[1] + '</li></ol>'
  return new_string

################################################################################

# Color schemes
color_schemes = {}
color_schemes['blue']   = ('eeeed2','6188b5')
color_schemes['brown']  = ('f0d9b5','b58863')
color_schemes['gray']   = ('c8c8c8','939393')
color_schemes['green']  = ('eeeed2','769656')
color_schemes['pink']   = ('eeeed2','f27372')
color_schemes['purple'] = ('eeeed2','c0a2c7')
