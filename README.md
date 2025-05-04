# chess-cards

This is a no-frills Command-line API that I wrote for creating Anki flashcards with chess position on a Mac. I make no claims about its portability to other systems. 

Each Anki deck for chess position data is associated with a yaml file. See `test.yaml` for an example. Here is a template showing the fields:

```
 card1:
  description: 
  fen: 
  instructions:
  solution: 
  difficulty: 
  tag: 
  movecheck:
```

- 'card1': This field is not used, but should be distinct for each card.
- 'fen': a fen string for the position (required)
- 'description': Description of the card, type of puzzle, where in the book it's from, etc. (optional)
- 'instructions': Instructions for the puzzle (optional; if not given, "White/Black to move" will be detected from the fen and used)
- 'solution': The solution to the puzzle (required)
- 'difficulty': easy/hard (optional; if not given, "easy" is assumed)
- 'tag': collection of words for creating special puzzle collections (optional)
- 'movecheck': True/False, whether to check for agreement between the fen and the solution for White/Black to move (optional; True is assumed if not given)

## Set up Anki

- Download and install the Anki app on your Mac from https://apps.ankiweb.net
- Open Anki. Create a profile with 'File > Switch Profile > Add'. Let's suppose your Profile is 'PaulMorphy'.
- Close Anki.

## Set up your Python environment for running the `cards.py` script

To avoid dependency issues in Python, you will need to create a virtual environment. Open a terminal window and type:
```
  $ python3 -m venv path/to/venv  # I used path/to/venv = '~/Chess/cards/env'
  $ source path/to/venv/bin/activate
  $ python3 -m pip install pyyaml
  $ python3 -m pip install unidecode
  $ python3 -m pip install anki
  $ python3 -m pip install chess
  $ exit
```
## Run the test script

To verify that everything is working correctly, create flashcards with data in the `test.yaml` file.
```
  $ ./cards.py PaulMorphy test.yaml -d "Test Deck"
```
Open Anki, and you should have two decks of cards: "Test Deck" and "Hard: Test Deck". 

_It is not necessary to create all of your flashcards before running the `cards.py` script._ The script will compare the card info in your yaml file with the info already stored in Anki, and it will only create cards that it hasn't seen. 

## Anki Settings for Chess Study

Personal preference will dictate how you adjust your Anki settings for chess study. I use the following:
- New cards/day: 5
- Maximum reviews/day: 10
- learning steps: 1m 2d
- Graduating interval: 2
- Easy interval: 4

***Happy Studying!***
