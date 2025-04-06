import math
from statistics import median

from statics import calculate_color


class MetricDataPoint:
    def __init__(self, mmr: int, power: int, world_rank: int = None, total_wins: int = None):
        self.world_rank = world_rank
        self.mmr = mmr
        self.power = power
        self.total_wins = total_wins if total_wins is not None else 0


class PlayerRecord:
    def __init__(self, id: str, timestamp, metrics: MetricDataPoint, name: str = None):
        self.id = id
        self.name = name
        self.metrics = metrics
        self.timestamp = timestamp


class PlayerStats:
    def __init__(self, start_record: PlayerRecord):
        self.id = start_record.id
        self.current_name = start_record.name
        self.aliases = set()
        self.records = [start_record]
        self.current_metrics = start_record.metrics
        self.max_metrics = start_record.metrics
        self.median_metrics = start_record.metrics
        self.min_metrics = start_record.metrics
        self.score = None
        self.score_rank = None
        self.color = "red"

    def update_metrics(self):
        self.records.sort(key=lambda r: r.timestamp)
        self.current_metrics = self.records[-1].metrics
        self.aliases = list({r.name for r in self.records if r.name != self.current_name})

        mmr_values = [r.metrics.mmr for r in self.records]
        power_values = [r.metrics.power for r in self.records]
        total_wins_values = [r.metrics.total_wins for r in self.records]

        self.max_metrics = MetricDataPoint(
            max(mmr_values),
            max(power_values),
            total_wins=max(total_wins_values)
        )
        self.median_metrics = MetricDataPoint(
            int(median(mmr_values)),
            int(median(power_values)),
            total_wins=int(median(total_wins_values))
        )
        self.min_metrics = MetricDataPoint(
            min(mmr_values),
            min(power_values),
            total_wins=min(total_wins_values)
        )

    def add_record(self, record: PlayerRecord):
        self.records.append(record)

    def calculate_score(self, max_metrics: MetricDataPoint, last_timestamp):
        if last_timestamp != self.records[-1].timestamp:
            self.score = -1  # unknown
            return
        loss_ratio = math.sqrt(math.sqrt(self.max_metrics.total_wins / (self.max_metrics.power / 600)))
        mmr_percentage = (self.current_metrics.mmr / max_metrics.mmr)
        power_percentage = (self.current_metrics.power / max_metrics.power)
        self.score = mmr_percentage * 9 + power_percentage * 1 - loss_ratio * 0.1


class Leaderboard:
    def __init__(self):
        self.players = {}
        self.max_metrics = MetricDataPoint(0, 0, 1, 0)
        self.min_metrics = MetricDataPoint(0, 0, 1, 0)
        self.last_timestamp = None
        self.timestamps = []

    def add_record(self, record: PlayerRecord):
        if record.id in self.players:
            self.players[record.id].add_record(record)
        else:
            self.players[record.id] = PlayerStats(record)

    def get_player(self, id):
        return self.players.get(id, None)

    def get_players(self):
        if any(player.score is None for player in self.players.values()):
            self.update_metrics()
        return sorted(self.players.values(), key=lambda p: p.score_rank)

    def update_metrics(self):
        self.last_timestamp = max(max(r.timestamp for r in p.records) for p in self.players.values())
        self.timestamps = sorted(set(
            record.timestamp for player in self.players.values() for record in player.records
        ))  # Unique sorted timestamps
        self.max_metrics = MetricDataPoint(
            max(p.max_metrics.mmr for p in self.players.values()),
            max(p.max_metrics.power for p in self.players.values()),
            world_rank=1,
            total_wins=max(p.max_metrics.total_wins for p in self.players.values())
        )
        self.min_metrics = MetricDataPoint(
            min(p.max_metrics.mmr for p in self.players.values()),
            min(p.max_metrics.power for p in self.players.values()),
            world_rank=200,
            total_wins=min(p.max_metrics.total_wins for p in self.players.values())
        )

        for player in self.players.values():
            player.update_metrics()
            player.calculate_score(self.max_metrics, self.last_timestamp)

        sorted_players = sorted(self.players.values(), key=lambda p: p.score, reverse=True)

        for score_rank, player in enumerate(sorted_players, start=1):
            player.score_rank = score_rank
            player.color = calculate_color(1 - float(score_rank) / len(sorted_players))
