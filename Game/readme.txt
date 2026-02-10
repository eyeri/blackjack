# Blackjack

Core game logic skeleton for a Blackjack game.
This repository contains the engine-level implementation (no UI).

## Project Structure

Game/
├── card.py        # Card representation (rank, suit)
├── deck.py        # Deck creation, shuffle, draw logic
├── hand.py        # Hand management and score calculation
├── engine.py      # Core blackjack game flow
├── engine_api.py  # Interface layer for external usage (UI / tests)
├── tests_manual.py# Manual test cases
├── templates/
│   └── need_index.html.txt  # UI placeholder (not functional)

## Scope

- This project focuses on **game logic only**
- No GUI or web interface is implemented
- UI / frontend will interact through `engine_api.py`

## Running

This project is not a standalone executable application.
Use `tests_manual.py` or import the engine modules for testing.

## Team Development Notes

- Do not modify function signatures without team discussion
- Core logic changes should be discussed before merging
- Use feature branches for development

## Setup

git clone https://github.com/eyeri/blackjack.git
cd blackjack
python -m pip install -r requirements.txt
