from engine import GameEngine, Phase

def print_state(snapshot):
    print(f"\n--- [Phase: {snapshot['phase']}] ---")
    print(f"Dealer Cards: {snapshot['dealer_cards']} (Total: {snapshot['dealer_total']})")
    print(f"Player Cards: {snapshot['player_cards']} (Total: {snapshot['player_total']})")
    print(f"Remaining Deck: {snapshot['deck_remaining']}")
    if snapshot['outcome_text']:
        print(f"Result: {snapshot['outcome_text']}")

def run_demo():
    engine = GameEngine()
    
    print("Game Start: Dealing cards...")
    engine.new_round()
    print_state(engine.state_snapshot())

    while engine.phase == Phase.PLAYER_TURN and engine.player.best_total() <= 16:
        print("\nPlayer: Action - HIT")
        engine.player_hit()
        print_state(engine.state_snapshot())

    if engine.phase == Phase.PLAYER_TURN:
        print("\nPlayer: Action - STAND")
        engine.player_stand()
        print_state(engine.state_snapshot())

if __name__ == "__main__":
    run_demo()