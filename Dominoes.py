from collections import defaultdict
from enum import Enum
import math
from fractions import Fraction

debug = False


class _Player(Enum):
    PLAYER_0 = 1
    PLAYER_1 = 2
    PLAYER_2 = 3
    PLAYER_3 = 4


class _Zone(Enum):
    ZONE_1 = 1
    ZONE_2 = 2
    ZONE_3 = 3
    ZONE_12 = 4
    ZONE_13 = 5
    ZONE_23 = 6
    ZONE_123 = 7


class Debug:
    def __init__(self, debug=True):
        self.debug = debug


class Player:
    def __init__(self, hand_size=7):
        self.hand_size = hand_size
        self.passed = {}


class Domino:
    def __init__(self, val1, val2):
        self.vals = [val1, val2]
        self.possible_owners = {
            _Player.PLAYER_0, _Player.PLAYER_1,
            _Player.PLAYER_2, _Player.PLAYER_3
        }
        self.id = hash(tuple(self.vals))

    def has(self, val: int):
        return val in self.vals

    def __repr__(self) -> str:
        return f'{self.vals}'

    def clear(self):
        self.possible_owners = []

    def remove(self, player):
        if player in self.possible_owners:
            self.possible_owners.remove(player)


class DominoesState():
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        self.active_ends = []
        if "_all_dominoes" not in self.__dict__:
            self._domino_map, self._all_dominoes = self.start_board()

    def start_board(self):
        domino_map = defaultdict(list)
        all_dominoes = []
        for i in range(7):
            for j in range(i, 7):
                domino = Domino(i, j)
                domino_map[i].append(domino)
                all_dominoes.append(domino)
                if i != j:
                    domino_map[j].append(domino)
        return domino_map, all_dominoes

    # I don't think this belongs here... this should just provide a get_domino_map and pass it
    # to maybe the board state? player state? and then have the following function there
    def get_connecting_dominoes_for_player(self, player, num):
        return [domino for domino in self._domino_map[num] if player in domino.possible_owners]

    def play_on_right(self, domino):
        if not self.active_ends:
            self.active_ends = domino.vals[::]
            return True
        if domino.vals[0] == self.active_ends[1]:
            self.active_ends[1] = domino.vals[1]
            return True
        elif domino.vals[1] == self.active_ends[1]:
            self.active_ends[1] = domino.vals[0]
            return True
        else:
            return False

    def play_on_left(self, domino):
        if not self.active_ends:
            self.active_ends = domino.vals[::]
            return True
        if domino.vals[0] == self.active_ends[0]:
            self.active_ends[0] = domino.vals[1]
            return True
        elif domino.vals[1] == self.active_ends[0]:
            self.active_ends[0] = domino.vals[0]
            return True
        else:
            return False


class PlayersState:
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        if "_all_players" not in self.__dict__:
            self._all_players = self.start_players()

    def start_players(self):
        return {_Player.PLAYER_0: Player(), _Player.PLAYER_1: Player(),
                _Player.PLAYER_2: Player(), _Player.PLAYER_3: Player()}

    def get_player(self, i):
        players = [_Player.PLAYER_0, _Player.PLAYER_1,
                   _Player.PLAYER_2, _Player.PLAYER_3]
        return players[i], self._all_players[players[i]]


class ZonesState:
    _self = None

    def __new__(cls, dominoes):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self, dominoes):
        if "_all_zones" not in self.__dict__:
            self._all_zones, self._domino_to_zone = self.make_zones(dominoes)

    def make_zones(self, all_dominoes):
        groups = {}
        domino_to_zone = {}
        for zone in _Zone:
            groups[zone] = []
        for domino in all_dominoes:
            groups[_Zone.ZONE_123].append(domino)
            domino_to_zone[domino] = _Zone.ZONE_123
        return groups, domino_to_zone

    def remove(self, domino):
        if self._domino_to_zone[domino] and domino in self._all_zones[self._domino_to_zone[domino]]:
            self._all_zones[self._domino_to_zone[domino]].remove(domino)
            domino.clear()
            self._domino_to_zone[domino] = None
        else:
            if self._domino_to_zone[domino]:
                print("ERROR REMOVING", self._domino_to_zone[domino],
                      domino, self._all_zones[self._domino_to_zone[domino]])

    def shift(self, domino, player):
        curr_zone_players = self.zone_to_players(self._domino_to_zone[domino])
        new_zone_players = set(curr_zone_players) - set([player])

        if curr_zone_players == new_zone_players:
            return
        if domino not in self._all_zones[self._domino_to_zone[domino]]:
            return
        domino.remove(player)
        self._all_zones[self._domino_to_zone[domino]].remove(domino)
        self._all_zones[self.players_to_zone(new_zone_players)].append(domino)
        self._domino_to_zone[domino] = self.players_to_zone(new_zone_players)

    def assignToP0(self, domino):
        self.remove(domino)

    def players_to_zone(self, players):
        singles = {_Player.PLAYER_1: _Zone.ZONE_1,
                   _Player.PLAYER_2: _Zone.ZONE_2, _Player.PLAYER_3: _Zone.ZONE_3}
        if len(players) == 1:
            return singles[players.copy().pop()]
        if players == set([_Player.PLAYER_1, _Player.PLAYER_2]):
            return _Zone.ZONE_12
        if players == set([_Player.PLAYER_2, _Player.PLAYER_3]):
            return _Zone.ZONE_23
        if len(players) == 3:
            return _Zone.ZONE_123
        else:
            return _Zone.ZONE_13

    def zone_to_players(self, zone):
        zone_players = {_Zone.ZONE_1: [_Player.PLAYER_1],
                        _Zone.ZONE_2: [_Player.PLAYER_2],
                        _Zone.ZONE_3: [_Player.PLAYER_3],
                        _Zone.ZONE_12: [_Player.PLAYER_1, _Player.PLAYER_2],
                        _Zone.ZONE_13: [_Player.PLAYER_1, _Player.PLAYER_3],
                        _Zone.ZONE_23: [_Player.PLAYER_2, _Player.PLAYER_3],
                        _Zone.ZONE_123: [_Player.PLAYER_1, _Player.PLAYER_2, _Player.PLAYER_3]}
        return zone_players[zone]

    def player_to_dominoes(self, player: _Player):
        return [domino for domino, _ in self._domino_to_zone.items() if player in domino.possible_owners]

    def print_zones(self):
        for zone, val in self._all_zones.items():
            if val:
                print(zone, val if True else len(val))


class Game:
    _self = None

    def __new__(cls):
        if cls._self is None:
            cls._self = super().__new__(cls)
        return cls._self

    def __init__(self):
        if "_dominoes_state" not in self.__dict__:
            self._dominoes_state = DominoesState()
            self._players_state = PlayersState()
            self._zones_state = ZonesState(self._dominoes_state._all_dominoes)
            self._round = 0

    def player_passed(self, numbers):
        player_name, _ = self.get_current_player()
        if player_name != _Player.PLAYER_0:
            for number in numbers:
                for domino in self._dominoes_state.get_connecting_dominoes_for_player(player_name, number):
                    print("player doesn't have this domino - ", domino)
                    self._zones_state.shift(domino, player_name)
        self._round += 1

    def play_right(self, domino):
        if self._dominoes_state.play_on_right(domino):
            self.domino_played(domino)
        else:
            print("CANT PLAY DOMINO")

    def play_left(self, domino):
        if self._dominoes_state.play_on_left(domino):
            self.domino_played(domino)
        else:
            print("CANT PLAY DOMINO")

    def domino_played(self, domino):
        _, player_stats = self.get_current_player()
        self._zones_state.remove(domino)
        player_stats.hand_size -= 1
        self._round += 1

    def assignToP0(self, dominos: [int]):
        for i in dominos:
            self._zones_state.assignToP0(self._dominoes_state._all_dominoes[i])

    def get_current_player(self):
        return self._players_state.get_player(self._round % 4)

    def print_possible_for_player(self, player):
        print([d for d in self._dominoes_state._all_dominoes if player in d.possible_owners], end="\n\n")

    def print_dominos_in_play(self):
        print([(i, d) for i, d in enumerate(
            self._dominoes_state._all_dominoes) if d.possible_owners], end="\n\n")

    def print_player_hands(self):
        for player, hand_stat in self._players_state._all_players.items():
            print(player, hand_stat.hand_size)

    def print_current_player(self):
        player_name, player_stats = self.get_current_player()
        print(
            f"Current Player -> {player_name} with hand size: {player_stats.hand_size}")


class Statistics:
    def __init__(self, zones: ZonesState, player_states: PlayersState):
        self.zones = zones
        self.players = player_states

    def zone_count(self, zone: _Zone, seen=0):
        # print("zc", max(self.zone_size(zone) - seen, 1))
        return self.zone_size(zone) - seen + 1

    def dominos_with_value(self, zone: _Zone, value: int):
        return len([domino for domino in self.zones._all_zones[zone] if domino.has(value)])

    def zone_size(self, zone: _Zone):
        return len(self.zones._all_zones[zone])

    def calculate_hand_range(self, total_round_count, zones):
        # player -> range -> value (in fraction)
        # player -> zone -> range -> value
        value_counts = defaultdict(int)
        value_counts_complement = defaultdict(int)
        this_turn_ranges = {}
        this_turn_ranges_complement = {}
        if debug:
            print("ROUNDROUNDROUND", total_round_count)
        for zone, choose in zones.items():
            if debug:
                print("TOTAL FOR THIS ZONE - ", math.comb(
                    self.zone_size(zone), choose), total_round_count, total_round_count / math.comb(
                    self.zone_size(zone), choose))
            if choose == 0:
                continue
            for domino_val in range(0, 7):
                if zone not in this_turn_ranges:
                    this_turn_ranges[zone] = {}
                    this_turn_ranges_complement[zone] = {}
                total_zone_count = self.zone_size(zone)
                if total_zone_count == 0:
                    continue
                val_zone_count = self.dominos_with_value(zone, domino_val)
                tzc = math.comb(
                    total_zone_count, choose)
                this_turn_ranges[zone][domino_val] = (
                    total_round_count - (math.comb(
                        total_zone_count - val_zone_count, choose) *
                        (total_round_count / tzc)))
                this_turn_ranges_complement[zone][domino_val] = (
                    math.comb(
                        total_zone_count - val_zone_count, choose) *
                    (total_round_count / tzc)
                )
        for domino_val in range(0, 7):
            probabilities = []
            probabilities_complement = []
            for zone in this_turn_ranges:
                if debug:
                    print("Domino Val: ", domino_val,
                          this_turn_ranges[zone][domino_val])
                if this_turn_ranges[zone][domino_val] > 0:
                    probabilities.append(
                        Fraction(int(this_turn_ranges[zone][domino_val]), total_round_count))
                    probabilities_complement.append(Fraction(
                        int(this_turn_ranges_complement[zone][domino_val]), total_round_count))
                    if debug:
                        print("asdfasdfa", this_turn_ranges[zone][domino_val])
                        print("asdfasdfa",
                              this_turn_ranges_complement[zone][domino_val])
                        print(total_round_count, "--------")
            if len(probabilities) == 1:
                value_counts[domino_val] = (
                    (total_round_count / probabilities[0].denominator) *
                    probabilities[0].numerator)
                value_counts_complement[domino_val] = ((total_round_count / probabilities_complement[0].denominator) *
                                                       probabilities_complement[0].numerator)
            if len(probabilities) == 2:
                l2res = UnionOf2(probabilities[0], probabilities[1])
                l2resc = UnionOfN(probabilities_complement)
                if debug:
                    print("probs", probabilities)
                    print("probs_complement", probabilities_complement)
                value_counts[domino_val] = (
                    (total_round_count / l2res.denominator) * l2res.numerator)
                value_counts_complement[domino_val] = (
                    (total_round_count / l2resc.denominator) * l2resc.numerator)
                if debug:
                    print(
                        "HERERERE", value_counts[domino_val], value_counts_complement[domino_val])
            if len(probabilities) == 3:
                l3res = UnionOf3(
                    probabilities[0], probabilities[1], probabilities[2])
                l3resc = UnionOfN(probabilities_complement)
                value_counts[domino_val] = (
                    (total_round_count / l3res.denominator) * l3res.numerator)
                value_counts_complement[domino_val] = (
                    total_round_count / l3resc.denominator) * l3resc.numerator
            if len(probabilities) == 4:
                l4res = UnionOf4(probabilities[0], probabilities[1],
                                 probabilities[2], probabilities[3])
                l4resc = UnionOfN(probabilities_complement)
                value_counts[domino_val] = (
                    (total_round_count / l4res.denominator) * l4res.numerator)
                value_counts_complement[domino_val] = (
                    total_round_count / l4resc.denominator) * l4resc.numerator

        return value_counts, value_counts_complement

    def calculate_probabilities_for_player(self, player: Player):
        def comb(s, chose):
            return max(math.comb(s, chose), 1)
        total_combinations = 0
        final_stats = {
            _Player.PLAYER_1: {i: 0 for i in range(7)},
            _Player.PLAYER_2: {i: 0 for i in range(7)},
            _Player.PLAYER_3: {i: 0 for i in range(7)}
        }

        for p1_from_z12 in range(self.zone_count(_Zone.ZONE_12)):
            for p1_from_z13 in range(self.zone_count(_Zone.ZONE_13)):
                for p1_from_z123 in range(self.zone_count(_Zone.ZONE_123)):
                    _, p1_stats = self.players.get_player(1)
                    remaining_h1 = p1_stats.hand_size - p1_from_z12 - p1_from_z13 - p1_from_z123
                    if remaining_h1 < 0 or remaining_h1 > len(self.zones._all_zones[_Zone.ZONE_1]):
                        continue
                    # finish implementing the rest of the algorithm, and then look through the combinations for each player
                    # calculate the combinations
                    for p2_from_z12 in range(self.zone_count(_Zone.ZONE_12, p1_from_z12)):
                        for p2_from_z23 in range(self.zone_count(_Zone.ZONE_23)):
                            for p2_from_z123 in range(self.zone_count(_Zone.ZONE_123, p1_from_z123)):
                                _, p2_stats = self.players.get_player(2)
                                _, p3_stats = self.players.get_player(3)
                                remaining_h2 = p2_stats.hand_size - p2_from_z12 - p2_from_z23 - p2_from_z123
                                if remaining_h2 < 0 or remaining_h2 > self.zone_size(_Zone.ZONE_2):
                                    continue
                                if p3_stats.hand_size > len(self.zones.player_to_dominoes(_Player.PLAYER_3)) - p1_from_z13 - p2_from_z23 - p1_from_z123 - p2_from_z123:
                                    continue
                                combinations_h1 = comb(self.zone_size(_Zone.ZONE_12), p1_from_z12) * comb(self.zone_size(_Zone.ZONE_13), p1_from_z13) * comb(
                                    self.zone_size(_Zone.ZONE_123), p1_from_z123) * comb(self.zone_size(_Zone.ZONE_1), remaining_h1)
                                p1combination = {_Zone.ZONE_12: p1_from_z12, _Zone.ZONE_13: p1_from_z13,
                                                 _Zone.ZONE_123: p1_from_z123, _Zone.ZONE_1: remaining_h1}
                                combinations_h2 = comb(self.zone_size(_Zone.ZONE_12) - p1_from_z12, p2_from_z12) * comb(self.zone_size(_Zone.ZONE_23), p2_from_z23) * comb(
                                    self.zone_size(_Zone.ZONE_123) - p1_from_z123, p2_from_z123) * comb(self.zone_size(_Zone.ZONE_2), remaining_h2)
                                combinations_h3 = comb(len(self.zones.player_to_dominoes(
                                    _Player.PLAYER_3)) - p1_from_z13 - p2_from_z23 - p1_from_z123 - p2_from_z123, p3_stats.hand_size)
                                p3_from_z13 = self.zone_size(
                                    _Zone.ZONE_13) - p1_from_z13
                                p3_from_z23 = self.zone_size(
                                    _Zone.ZONE_23) - p2_from_z23
                                p3_from_z123 = self.zone_size(
                                    _Zone.ZONE_123) - p1_from_z123 - p2_from_z123
                                remaining_h3 = len(self.zones.player_to_dominoes(_Player.PLAYER_3)) - p1_from_z13 - \
                                    p2_from_z23 - p1_from_z123 - p2_from_z123 - \
                                    p3_from_z123 - p3_from_z13 - p3_from_z23
                                print(self.zone_size(_Zone.ZONE_123),
                                      p1_from_z13, p2_from_z123, p3_from_z123)
                                # p2 combination stats
                                p2combination = {_Zone.ZONE_12: p2_from_z12, _Zone.ZONE_23: p2_from_z23,
                                                 _Zone.ZONE_123: p2_from_z123, _Zone.ZONE_2: remaining_h2}
                                # p3 combination stats
                                p3combination = {_Zone.ZONE_13: p3_from_z13, _Zone.ZONE_23: p3_from_z23,
                                                 _Zone.ZONE_123: p3_from_z123, _Zone.ZONE_3: remaining_h3}
                                total_combinations += combinations_h1 * combinations_h2 * combinations_h3
                                this_round_combinations = combinations_h1 * combinations_h2 * combinations_h3

                                _, p1_combinations_complement = self.calculate_hand_range(
                                    this_round_combinations, p1combination)
                                _, p2_combinations_complement = self.calculate_hand_range(
                                    this_round_combinations, p2combination)
                                _, p3_combinations_complement = self.calculate_hand_range(
                                    this_round_combinations, p3combination)
                                for curr_player, player_stats_result in {_Player.PLAYER_1: p1_combinations_complement,
                                                                         _Player.PLAYER_2: p2_combinations_complement,
                                                                         _Player.PLAYER_3: p3_combinations_complement}.items():
                                    for val, count in player_stats_result.items():
                                        final_stats[curr_player][val] += this_round_combinations - count

                                if debug:
                                    print("isaac", p1combination)
                                    print("isaac", p2combination)
                                    print("isaac", p3combination)

                                    # print("value_combinations", {val: (count/total_combinations) * 100 for val, count in value_combinations_p1.items()})
                                    print("complements p1- ", {val: [(1 - (count/this_round_combinations)) * 100,
                                          this_round_combinations - count] for val, count in p1_combinations_complement.items()})
                                    print("complements p2- ", {val: [(1 - (count/this_round_combinations)) * 100,
                                          this_round_combinations - count] for val, count in p2_combinations_complement.items()})
                                    print("complements p3- ", {val: [(1 - (count/this_round_combinations)) * 100,
                                          this_round_combinations - count] for val, count in p3_combinations_complement.items()})


        for player in final_stats:
            print({valll: (counttt/total_combinations)*100 for valll,
                  counttt in final_stats[player].items()})
        print("here", total_combinations)
        print("other way: ", )


def main():

    _game = Game()
    _game.print_dominos_in_play()
    _game.assignToP0([0, 7, 13, 18, 22, 25, 27])

    _game._zones_state.print_zones()
    _all_dominoes = _game._dominoes_state._all_dominoes

    stats = Statistics(_game._zones_state, _game._players_state)
    stats.calculate_probabilities_for_player(_Player.PLAYER_1)
    # _game.play_left(_all_dominoes[27])  # 6/6
    # _game.print_dominos_in_play()

    # _game.play_left(_all_dominoes[6])  # 6/6
    # _game.play_right(_all_dominoes[21])  # 6/6
    # _game.play_left(_all_dominoes[2])  # 6/6

    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)

    # _game.play_right(_all_dominoes[9])  # 6/6
    # _game.play_right(_all_dominoes[1])  # 6/6
    # _game.play_left(_all_dominoes[13])  # 6/6
    # _game.play_left(_all_dominoes[8])  # 6/6

    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)

    # _game.play_right(_all_dominoes[0])  # 6/6
    # _game.play_right(_all_dominoes[3])  # 6/6
    # _game.play_left(_all_dominoes[10])  # 6/6
    # _game.play_left(_all_dominoes[4])  # 6/6

    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)

    # _game.play_right(_all_dominoes[18])  # 6/6
    # _game.play_right(_all_dominoes[19])  # 6/6
    # _game.play_right(_all_dominoes[23])  # 6/6
    # _game.play_left(_all_dominoes[5])  # 6/6
    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)

    # _game.play_left(_all_dominoes[16])  # 6/6
    # _game.play_left(_all_dominoes[15])  # 6/6
    # _game.play_right(_all_dominoes[25])  # 6/6
    # _game.play_right(_all_dominoes[11])  # 6/6
    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)




# asdfasdfasdfasdfa



    # _game.play_left(_all_dominoes[10]) # 6/6
    # _game.play_left(_all_dominoes[11]) # 6/6
    # _game.player_passed([5,0]) # skip
    # _game.player_passed([5,0]) # skip

    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)
    # _game.print_dominos_in_play()
    # _game._zones_state.print_zones()

    # _game.play_right(_all_dominoes[1]) # 6/6
    # _game.play_left(_all_dominoes[16]) # 6/6
    # _game.play_right(_all_dominoes[7]) # skip
    # _game.play_left(_all_dominoes[14]) # 6/6

    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)
    # _game.print_dominos_in_play()
    # _game._zones_state.print_zones()

    # _game.player_passed([1,2]) # skip
    # _game._zones_state.print_zones()
    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)
    # # _game.print_current_player() # p2
    # _game.play_left(_all_dominoes[-1]) # 6/6
    # _game._zones_state.print_zones()
    # # print("========================")

    # # _game.print_current_player() # p2
    # _game.player_passed([6]) # skip
    # # _game._zones_state.print_zones()
    # print("========================")

    # # _game.print_current_player() # p3
    # _game.play_right(_all_dominoes[-2]) # 5/6
    # # _game._zones_state.print_zones()
    # print("========================")

    # # _game.print_current_player() # p4
    # _game.play_left(_all_dominoes[-3]) # 5/5
    # _game.play_right(_all_dominoes[-3]) # 5/5
    # # _game._zones_state.print_zones()
    # print("========================")

    # # _game.print_current_player() # p1
    # _game.play_left(_all_dominoes[-5]) # 4/5
    # _game.play_right(_all_dominoes[-5]) # 4/5
    # # _game._zones_state.print_zones()
    # print("========================")

    # # _game.print_current_player() # p2
    # _game.play_right(_all_dominoes[-9]) # 3/4
    # # _game._zones_state.print_zones()
    # print("========================")

    # # _game.print_current_player()# p3
    # _game.player_passed([3,6]) # skip
    # # _game._zones_state.print_zones()

    # stats.calculate_probabilities_for_player(_Player.PLAYER_1)


"""

Things to measure:

 (1) The composition of the players' hand in terms of
   how many they're most likely to have from a
   certain section?

 (2) The range of values they have and the probabilities
   matched up with those ranges.

 (3) Plan probability of an individual domino being
   in a specific person's hand

   

Algorithms:
 (1) have something that keeps track of "domino count from zone frequency for player"
     player_hand -> zone_count -> possible_count -> value
     (paired with total cominations, we can find the most likely make up)

     When we get to the part where we calculate combinations -
     For each player
       For each zone they own
         We add the total number of combinations for that round
         to the possible count attribute of zone_count associated
         with the count in that zone

    eg:
        1/2-2 1/3-0 1/2/3-0, 1-1
        1/2-0 2/3-0 1/2/3-2 2-1
        1/3-0 2/3-1 1/2/3-1 3-1
        3

        "domino count from zone frequency for player":
        {
            player1 : {             <- default dict 
                1/2 :{
                  (possibly2) : 3
                }
                1/3 :{
                  (possibly0) : 3
                }
                1/2/3 : {
                  (possibly0) : 3
                }
                1 : {
                  (possibly1) : 3
                }
            }
            player2 : {             <- default dict 
                1/2 :{
                  (possibly0) : 3
                }
                2/3 :{
                  (possibly0) : 3
                }
                1/2/3 : {
                  (possibly2) : 3
                }
                2 : {
                  (possibly1) : 3
                }
            }
            player3 : {             <- default dict 
                1/3 :{
                  (possibly0) : 3
                }
                2/3 :{
                  (possibly1) : 3
                }
                1/2/3 : {
                  (possibly1) : 3
                }
                3 : {
                  (possibly1) : 3
                }
            }
        }

        After building the map, we can now say, what's the most
        likely composition for p1-3? And then we just go through
        the zones, and through the possible things, and pick the one
        with the highest count, and then show it as a fraction. We
        can figure out how exactly to implement it, and since it's a
        UI thing we can show a lot, so for now, just have it list all
        things in order of most likely to least likely for each player.

 (2) Find out which dominoes are in each group (have the zone to
     domino thing on hand). Similar to above, but we're looping through
     players' combinations, and zones within that combination. Then
     for each digit, (we know how many combinations there were for each zone
     so we just subtract the combinations that didn't include a certain number)

     Find out how many dominoes contains the current value. Remove those. Then
     from the remaining pile, calculate how many combinations where we take
     what we were supposed to take. Now, subtract the total round combination, with
     that combination to get the number of combinations with dominoes with the value
     we're looking for. That result over the total count for that round is the percentage
     FOR THAT ZONE. After getting all of the zones, were do  P(A∩B). To get
     the actual probability for that ROUND.

     Add each individually with same denominator blah blah


     NOTE - if the solo set has numbers, those will always be 100%
    
"""


# def calculate_hand_range(total_round_count, zones):
#     # player -> range -> value (in fraction)

#     # player -> zone -> range -> value

#     this_turn_ranges = {}
#     for zone in zones:
#         for domino_val in range(0, 7):
#             total_zone_count = zone.get_domino_total(zone)
#             val_zone_count = zone.get_dominoes_with_val(zone, domino_val)
#             this_turn_ranges[zone][domino_val] = (
#                 total_round_count - math.comb(
#                     total_zone_count - val_zone_count, choose) *
#                     (total_round_count / total_zone_count))
#     for domino_val in range(0, 7):
#         probabilities = []
#         for zone in this_turn_ranges:
#             if zone[domino_val] > 0:
#                 probabilities += Fraction(zone[domino_val], total_round_count)
#         if len(probabilities) == 1:
#             this_turn_ranges[domino_val] = (
#                 (total_round_count / probabilities[0].denominator) *
#                     probabilities[0].numerator)
#         if len(probabilities) == 2:
#             l2res = UnionOf2(probabilities[0], probabilities[1])
#             this_turn_ranges[domino_val] = (
#                 (total_round_count / l2res.denominator) * l2res.numerator)
#         if len(probabilities) == 3:
#             l3res = UnionOf3(probabilities[0], probabilities[1], probabilities[2])
#             this_turn_ranges[domino_val] = (
#                 (total_round_count / l3res.denominator) * l3res.numerator)
#         if len(probabilities) == 4:
#             l4res = UnionOf4(probabilities[0], probabilities[1],
#                         probabilities[2], probabilities[3])
#             this_turn_ranges[domino_val] = (
#                 (total_round_count / l4res.denominator) * l4res.numerator)
#     print(this_turn_ranges)


def Certain(*fractions: Fraction):
    for fraction in fractions:
        if fraction > 1:
            return True
    return False


def UnionOf2(a: Fraction, b: Fraction):
    if Certain(a, b):
        return max(a.denominator, b.denominator)
    return a + b - (a * b)


def UnionOf3(a: Fraction, b: Fraction, c: Fraction):
    if Certain(a, b, c):
        return max(a.denominator, b.denominator, c.denominator)
    return a + b + c - (a * b) - (a * c) - (b * c) + (a * b * c)


def UnionOf4(a: Fraction, b: Fraction, c: Fraction, d: Fraction):
    if Certain(a, b, c, d):
        return max(a.denominator, b.denominator,
                   c.denominator, d.denominator)
    return (a + b + c + d -
            (a * b) - (a * c) - (a * d) - (b * c) - (b * d) - (c * d)
            + (a * b * c) + (a * b * d) + (a * c * d) + (b * c * d) -
            (a * b * c * d))


def UnionOfN(probabilities):
    product = 1
    for probability in probabilities:
        product *= probability
    if debug:
        print("The complement product - ", product)
    return product


def yield_test(A, B, C):
    for a in range(A):
        for b in range(B):
            for c in range(C):
                yield a, b, c



main()


def iterate_through_subsets():
    pass
