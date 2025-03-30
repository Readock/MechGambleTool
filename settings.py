import json
import os
from datetime import datetime
import statics
from leaderboard import Leaderboard, PlayerRecord, MetricDataPoint

RECORDS_FILE = "records.json"
SETTINGS_FILE = "settings.json"

defaultSettings = {
    "game_dir": "C:\\Program Files(x86)\\Steam\\steamapps\\common\\Mechabellum"
}


def game_filepath():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                log_path = os.path.join(data.get("game_dir", defaultSettings["game_dir"]))
            except json.JSONDecodeError:
                log_path = defaultSettings["game_dir"]
    else:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(defaultSettings, file, indent=4)
        log_path = defaultSettings["game_dir"]

    if not os.path.exists(log_path):
        statics.show_error(f"Could not find game folder! Please change in the settings.json file",
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
