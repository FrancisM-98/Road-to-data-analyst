# Implementation Plan - Flip 7 (Negotiation Edition)

## Goal
Create a Python-based command-line version of Flip 7 that supports a custom "Negotiation" rule, allowing players to trade cards to avoid busting.

## User Review Required
> [!NOTE]
> **Negotiation Trigger**: Negotiations can now be initiated **Anytime** (Start of turn, or interrupts like Bust).
> **Action Space**: Players can offer Cards for Cards, or Card for Safety (redraw).
> **Interface**: CLI will prompt for actions `[H]it`, `[S]tay`, `[N]egotiate`.

## Proposed Changes

### New Directory: `VS_Code/Python/Flip7/`

#### [NEW] [models.py](file:///c:/Users/FrancisMultani/Desktop/VS_Code/Python/Flip7/models.py)
- `Card`: Class representing a card (Value 0-12, Special Types).
- `Deck`: Handles generation and shuffling of the specific Flip 7 distribution.
- `Player`: Tracks hand, hand count, current round points, total score. Methods to add/remove cards.

#### [NEW] [game.py](file:///c:/Users/FrancisMultani/Desktop/VS_Code/Python/Flip7/game.py)
- `Flip7Game`: Main controller.
- `start_round()`: Resets hands.
- `play_turn(player)`: The main decision loop. Now allows `Negotiate` action at start of turn.
- `initiate_negotiation(active_player)`: **New!** Interactive wizard to build a trade offer (Give/Swap).
- `check_bust(player, card)`: Detects duplicates.
- `resolve_bust_negotiation(player, card)`: Specific "Save me!" negotiation phase triggered on bust.

#### [NEW] [main.py](file:///c:/Users/FrancisMultani/Desktop/VS_Code/Python/Flip7/main.py)
- Game loop entry point.
- CLI Interface: parsing commands like `hit`, `stay`, `trade`.

## Verification Plan

### Automated Tests
- None planned initially (rapid prototype).

### Manual Verification
1.  **Run the Game**: `python main.py`
2.  **Simulate Bust**:
    - Force a scenario (or play until) a player draws a duplicate.
    - Verify the "Negotiation" prompt appears.
3.  **Execute Trade**:
    - Select an opponent to give the card to.
    - Verify opponent receives the card.
    - Verify active player stays in the round and draws a new card.
4.  **Check Win Condition**:
    - Verify Flip 7 (7 unique cards) awards bonus +15.
    - Verify Score 200 ends game.
