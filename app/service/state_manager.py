from typing import List

from app import statics
from app.leaderboard.leaderboard import Leaderboard, PlayerStats


class StateManager:
    _instance = None
    leaderboard: Leaderboard = None
    players: List[PlayerStats] = []
    selected_players: List[PlayerStats] = []
    left_players: List[PlayerStats] = []
    right_players: List[PlayerStats] = []
    current_bet = 0

    def __init__(self, leaderboard):
        self.leaderboard = leaderboard
        self.players = leaderboard.get_players()

    @classmethod
    def init(cls, leaderboard):
        if cls._instance is None:
            cls._instance = cls(leaderboard)

    @classmethod
    def instance(cls) -> "StateManager":
        if cls._instance is None:
            raise RuntimeError("StateManager not initialized!")
        return cls._instance

    def reset_selected_players(self):
        self.selected_players = []
        self.left_players = []
        self.right_players = []
        self.current_bet = 0

    def has_selected_players(self):
        return len(self.left_players) > 0 or len(self.right_players) > 0

    def has_selection_warnings(self):
        # check if selected players are up-to-date
        left = len(self.left_players) > 0 and all(not p.is_top_player for p in self.left_players)
        right = len(self.right_players) > 0 and all(not p.is_top_player for p in self.right_players)
        return left or right

    def select_players(self, smart: [PlayerStats] = None, left: [PlayerStats] = None, right: [PlayerStats] = None):
        if left:
            self.selected_players.extend(sorted(left, key=lambda p: p.score_rank))
            self.left_players.extend(sorted(left, key=lambda p: p.score_rank))
        if right:
            self.selected_players.extend(sorted(right, key=lambda p: p.score_rank))
            self.right_players.extend(sorted(right, key=lambda p: p.score_rank))
        if smart:
            self.selected_players.extend(sorted(smart, key=lambda p: p.score_rank))
            if len(self.left_players) < 1 and len(smart) > 0:
                self.left_players.append(smart[0])
                if len(self.right_players) < 1 < len(smart):
                    self.right_players.append(smart[1])
            elif len(self.right_players) < 1 and len(smart) > 0:
                self.right_players.append(smart[0])

    def unselect_player(self, player_or_id: int | PlayerStats):
        self.selected_players[:] = [player for player in self.selected_players if
                                    player.id != player_or_id and player_or_id != player]
        self.left_players[:] = [player for player in self.left_players if
                                player.id != player_or_id and player_or_id != player]
        self.right_players[:] = [player for player in self.right_players if
                                 player.id != player_or_id and player_or_id != player]

    def left_name(self):
        if len(self.left_players) > 0:
            return self.left_players[0].current_name
        return "Blue"

    def right_name(self):
        if len(self.right_players) > 0:
            return self.right_players[0].current_name
        return "Blue"

    def player_score_ratio(self):
        left = max(max((p.score for p in self.left_players), default=0.01), 0.01)
        right = max(max((p.score for p in self.right_players), default=0.01), 0.01)
        left_normal = max(left - self.leaderboard.min_score, 0.01)
        right_normal = max(right - self.leaderboard.min_score, 0.01)
        ratio = statics.clamp(float(left_normal) / (float(right_normal) + float(left_normal)), 0.1, 0.99)
        # if ratio > 0.5:
        #     # exaggerate ratio to see difference
        #     return math.sqrt(ratio - 0.5) * math.sqrt(0.5) + 0.5
        # if ratio < 0.5:
        #     # exaggerate ratio to see difference
        #     return -math.sqrt(ratio * -1 + 0.5) * math.sqrt(0.5) + 0.5
        return ratio

    def player_mmr_ratio(self):
        left = max(max((p.current_metrics.mmr for p in self.left_players), default=0.01), 0.01)
        right = max(max((p.current_metrics.mmr for p in self.right_players), default=0.01), 0.01)
        left_normal = max(left - self.leaderboard.min_metrics.mmr, 0.01)
        right_normal = max(right - self.leaderboard.min_metrics.mmr, 0.01)
        ratio = statics.clamp(float(left_normal) / (float(right_normal) + float(left_normal)), 0.1, 0.99)
        return ratio
