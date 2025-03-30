import json
import os
from datetime import datetime
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from log_importer import extract_leaderboard_data
from leaderboard import Leaderboard, PlayerRecord, MetricDataPoint

RECORDS_FILE = "records.json"
SETTINGS_FILE = "settings.json"

defaultSettings = {
    "game_dir": "C:\\Program Files(x86)\\Steam\\steamapps\\common\\Mechabellum"
}


def get_log_filepath():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                return data.get("log_filepath",
                                "C:\\Program Files(x86)\\Steam\\steamapps\\common\\Mechabellum") + "\\ProjectDatas\\Log"
            except json.JSONDecodeError:
                print("Error loading settings.json. Using default log path.")
    else:
        with open(SETTINGS_FILE, "w") as file:
            json.dump(defaultSettings, file, indent=4)
    return "C:\\Program Files(x86)\\Steam\\steamapps\\common\\Mechabellum\\ProjectDatas\\Log"


def get_log_filepath():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                log_path = os.path.join(data.get("game_dir", defaultSettings["game_dir"]), "ProjectDatas",
                                        "Log")
            except json.JSONDecodeError:
                log_path = os.path.join(defaultSettings["game_dir"], "ProjectDatas", "Log")
    else:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
            json.dump(defaultSettings, file, indent=4)
        log_path = os.path.join(defaultSettings["game_dir"], "ProjectDatas", "Log")

    if not os.path.exists(log_path):
        show_error_and_exit(f"Could not find game folder! Please change in the settings.json file")

    return log_path


def show_error_and_exit(message):
    app = QApplication(sys.argv)
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setText(message)
    msg_box.setWindowTitle("Error")
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
    sys.exit(1)  # Exit the application


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
