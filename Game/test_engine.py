import pytest
from Game.card import Card
from Game.hand import Hand
from Game.engine import GameEngine, Phase


def c(code: str) -> Card:
    return Card(rank=code[:-1], suit=code[-1])


def make_hand(*codes: str) -> Hand:
    hand = Hand()
    for code in codes:
        hand.add(c(code))
    return hand


def rig_draws(engine: GameEngine, *codes: str) -> None:
    """
    Deck.draw() uses pop() from the end.
    rig_draws(engine, "3D", "5C") means:
      first draw -> 5C
      second draw -> 3D
    """
    engine.deck.cards = [c(code) for code in codes]


@pytest.mark.parametrize(
    "player_codes, dealer_codes, expected",
    [
        (("10H", "9S"), ("10D", "8C"), "WIN"),
        (("10H", "8S"), ("10D", "9C"), "LOSE"),
        (("10H", "8S"), ("9D", "9C"), "PUSH"),
        (("AH", "KS"), ("10D", "9C"), "BLACKJACK"),
        (("10H", "8S"), ("AD", "KC"), "LOSE"),
        (("10H", "8S"), ("9D", "7C", "8H"), "WIN"),
    ],
)
def test_evaluate_hand_cases(player_codes, dealer_codes, expected):
    engine = GameEngine(num_players=1)
    player_hand = make_hand(*player_codes)
    dealer_hand = make_hand(*dealer_codes)
    assert engine._evaluate_hand(player_hand, dealer_hand) == expected


def test_blackjack_payout_is_3_to_2():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.DEALER_TURN
    engine.player_balances = [900]      # main bet already deducted
    engine.player_bets = [[100]]
    engine.players = [[make_hand("AH", "KS")]]
    engine.dealer = make_hand("9D", "7C")
    engine.outcome_texts = [[""]]

    engine.resolve_round()

    assert engine.outcome_texts[0][0] == "BLACKJACK"
    assert engine.player_balances[0] == 1150  # 900 + 250


def test_normal_win_pays_1_to_1():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.DEALER_TURN
    engine.player_balances = [900]
    engine.player_bets = [[100]]
    engine.players = [[make_hand("10H", "9S")]]
    engine.dealer = make_hand("10D", "7C")
    engine.outcome_texts = [[""]]

    engine.resolve_round()

    assert engine.outcome_texts[0][0] == "WIN"
    assert engine.player_balances[0] == 1100


def test_push_returns_original_bet():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.DEALER_TURN
    engine.player_balances = [900]
    engine.player_bets = [[100]]
    engine.players = [[make_hand("10H", "8S")]]
    engine.dealer = make_hand("9D", "9C")
    engine.outcome_texts = [[""]]

    engine.resolve_round()

    assert engine.outcome_texts[0][0] == "PUSH"
    assert engine.player_balances[0] == 1000


def test_surrender_returns_half_bet_immediately():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.PLAYER_TURN
    engine.player_balances = [900]
    engine.player_bets = [[100]]
    engine.players = [[make_hand("10H", "6S")]]
    engine.outcome_texts = [[""]]
    engine.current_player_index = 0
    engine.current_hand_index = 0

    engine.player_surrender()

    assert engine.player_balances[0] == 950
    assert engine.outcome_texts[0][0] == "SURRENDER"


def test_split_creates_second_hand_and_charges_second_bet():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.PLAYER_TURN
    engine.player_balances = [900]
    engine.player_bets = [[100]]
    engine.players = [[make_hand("8H", "8S")]]
    engine.outcome_texts = [[""]]
    engine.current_player_index = 0
    engine.current_hand_index = 0

    rig_draws(engine, "5C", "3D")  # current hand gets 3D, new hand gets 5C
    engine.player_split()

    assert len(engine.players[0]) == 2
    assert len(engine.players[0][0].cards) == 2
    assert len(engine.players[0][1].cards) == 2
    assert engine.player_bets[0] == [100, 100]
    assert engine.player_balances[0] == 800


def test_resplit_allowed_until_four_hands():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.PLAYER_TURN
    engine.player_balances = [700]
    engine.players = [[
        make_hand("5H", "6S"),
        make_hand("8C", "8D"),
        make_hand("2H", "3S"),
    ]]
    engine.player_bets = [[100, 100, 100]]
    engine.outcome_texts = [["", "", ""]]
    engine.current_player_index = 0
    engine.current_hand_index = 1

    assert engine.can_split() is True


def test_resplit_blocked_after_four_hands():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.PLAYER_TURN
    engine.player_balances = [600]
    engine.players = [[
        make_hand("5H", "6S"),
        make_hand("8C", "8D"),
        make_hand("2H", "3S"),
        make_hand("4H", "4D"),
    ]]
    engine.player_bets = [[100, 100, 100, 100]]
    engine.outcome_texts = [["", "", "", ""]]
    engine.current_player_index = 0
    engine.current_hand_index = 1

    assert engine.can_split() is False


def test_double_down_allowed_on_split_hand():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.PLAYER_TURN
    engine.player_balances = [700]
    engine.players = [[
        make_hand("8H", "3S"),
        make_hand("8C", "2D"),
    ]]
    engine.player_bets = [[100, 100]]
    engine.outcome_texts = [["", ""]]
    engine.current_player_index = 0
    engine.current_hand_index = 1

    assert engine.can_double_down() is True


def test_insurance_pays_when_dealer_has_blackjack():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.INSURANCE
    engine.player_balances = [900]      # main bet already deducted
    engine.player_bets = [[100]]
    engine.players = [[make_hand("10H", "9S")]]
    engine.outcome_texts = [[""]]
    engine.insurance_bets = [0]
    engine.insurance_decided = [False]
    engine.dealer = make_hand("KD", "AS")  # second card is visible upcard Ace, dealer has blackjack

    engine.decide_insurance(0, True)

    assert engine.phase == Phase.ROUND_OVER
    assert engine.outcome_texts[0][0] == "LOSE"
    assert engine.player_balances[0] == 1000
    # 900 - 50 insurance + 150 insurance payout = 1000


def test_insurance_lost_when_dealer_not_blackjack_and_turn_continues():
    engine = GameEngine(num_players=1)
    engine.phase = Phase.INSURANCE
    engine.player_balances = [900]
    engine.player_bets = [[100]]
    engine.players = [[make_hand("10H", "7S")]]
    engine.outcome_texts = [[""]]
    engine.insurance_bets = [0]
    engine.insurance_decided = [False]
    engine.dealer = make_hand("9D", "AS")  # upcard Ace, but not blackjack

    engine.decide_insurance(0, True)

    assert engine.phase == Phase.PLAYER_TURN
    assert engine.player_balances[0] == 850
    assert engine.insurance_bets[0] == 50


def test_start_betting_round_reshuffles_when_shoe_low():
    engine = GameEngine(num_players=1)
    engine.player_ready = [True]
    engine.deck.cards = [c("AS")] * 10

    engine.start_betting_round()

    assert engine.phase == Phase.BETTING
    assert len(engine.deck.cards) == 312   # 6 * 52