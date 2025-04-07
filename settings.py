import json
import os
from datetime import datetime
import statics
from leaderboard import Leaderboard, PlayerRecord, MetricDataPoint

RECORDS_FILE = "records.json"
SETTINGS_FILE = "settings.json"

__settings = None


class Settings:
    def __init__(self, game_dir=None, fuzzy_threshold=None, favorite_bets=None, click_delay=None):
        self.game_dir = game_dir or "C:\\Program Files(x86)\\Steam\\steamapps\\common\\Mechabellum"
        self.fuzzy_threshold = fuzzy_threshold or 75
        self.favorite_bets = favorite_bets or [1, 3, 5 ,10, 200]
        self.click_delay = click_delay or 0.2

    def to_dict(self):
        """Convert settings object to dictionary."""
        return {
            "game_dir": self.game_dir,
            "fuzzy_threshold": self.fuzzy_threshold,
            "favorite_bets": self.favorite_bets,
            "click_delay": self.click_delay
        }

    @classmethod
    def from_dict(cls, data):
        """Create a Settings object from a dictionary."""
        return cls(
            game_dir=data.get("game_dir"),
            fuzzy_threshold=data.get("fuzzy_threshold"),
            favorite_bets=data.get("favorite_bets"),
            click_delay=data.get("click_delay")
        )

    def save(self, path="settings.json"):
        """Save current settings to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4)


def get_settings():
    global __settings
    if __settings is not None:
        return __settings
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                __settings = Settings.from_dict(data)
            except json.JSONDecodeError:
                # default settings
                __settings = Settings()
    else:
        __settings = Settings()
    __settings.save()
    return __settings


def game_filepath():
    log_path = get_settings().game_dir

    if not os.path.exists(log_path):
        statics.show_error(f"Could not find game folder at: {log_path}. Please change it in the settings.json file",
                           exitApp=True)

    return log_path


def game_log_filepath():
    return os.path.join(game_filepath(), "ProjectDatas", "Log")


def load_leaderboard():
    if os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return parse_leaderboard(data)
            except json.JSONDecodeError:
                print("Error loading " + RECORDS_FILE + ". Using empty leaderboard.")
    return Leaderboard()


def parse_leaderboard(data):
    leaderboard = Leaderboard()
    for player_data in data.get("players", {}).values():
        player_records = player_data.get("records", [])
        for record in player_records:
            record_obj = PlayerRecord(
                id=record["id"],
                timestamp=datetime.strptime(record["timestamp"], "%Y-%m-%d %H:%M:%S"),
                metrics=MetricDataPoint(
                    mmr=record["metrics"]["mmr"],
                    power=record["metrics"]["power"],
                    world_rank=record["metrics"].get("world_rank", 0),
                    total_wins=record["metrics"].get("total_wins", 0),
                ),
                name=record["name"],
            )
            leaderboard.add_record(record_obj)
    return leaderboard


def save_leaderboard(leaderboard):
    data = {
        "players": {
            player_id: {
                "current_name": player.current_name,
                "records": [
                    {
                        "id": record.id,
                        "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "metrics": {
                            "mmr": record.metrics.mmr,
                            "power": record.metrics.power,
                            "world_rank": record.metrics.world_rank,
                            "total_wins": record.metrics.total_wins,
                        },
                        "name": record.name,
                    }
                    for record in player.records
                ],
            }
            for player_id, player in leaderboard.players.items()
        }
    }
    with open(RECORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
