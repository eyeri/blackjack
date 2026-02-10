from engine import GameEngine


def print_state(g: GameEngine, title: str = ""):
    if title:
        print(f"\n=== {title} ===")
    s = g.state_snapshot(hide_dealer_hole=True)
    for k, v in s.items():
        print(f"{k}: {v}")


def demo():
    g = GameEngine()

    g.new_round()
    print_state(g, "New Round")

    # Manual demo flow (edit as needed)
    if g.can_hit():
        g.player_hit()
        print_state(g, "After HIT")

    if g.can_stand():
        g.player_stand()
        print_state(g, "After STAND (Round Over)")


if __name__ == "__main__":
    demo()
