import os
import re
import json
from datetime import datetime

import statics
from leaderboard import Leaderboard, PlayerRecord, MetricDataPoint


def extract_leaderboard_data(log_folder):
    leaderboard = Leaderboard()
    pattern = re.compile(
        r"\[Info]\[(\d{2}:\d{2}:\d{2}) (\d{4}/\d{2}/\d{2}).*] recv message \[\d+] - \[ResponseRankList]")

    for filename in os.listdir(log_folder):
        if filename.endswith(".txt"):
            with open(os.path.join(log_folder, filename), "r", encoding="utf-8") as file:
                lines = file.readlines()
                process_log(lines, leaderboard, pattern)

    return leaderboard


def process_log(lines, leaderboard, pattern):
    for i, line in enumerate(lines):
        match = pattern.match(line.strip())
        if match:
            time_part, date_part = match.groups()
            timestamp = datetime.strptime(f"{date_part} {time_part}", "%Y/%m/%d %H:%M:%S")
            json_data = extract_json_data(lines[i + 1:])
            if json_data:
                if "players" not in json_data or len(json_data["players"]) != 200:
                    statics.show_error("Failed parsing log leaderboard json!\nDid not have expected 200 players")
                else:
                    update_leaderboard(json_data, leaderboard, timestamp)


def extract_json_data(json_lines):
    data = []
    for line in json_lines:
        data.append(line.strip())
        try:
            return json.loads("".join(data))[0]
        except json.JSONDecodeError:
            continue
    return None


def update_leaderboard(leaderboard_json, leaderboard, timestamp):
    if isinstance(leaderboard_json, dict) and "players" in leaderboard_json:
        if leaderboard_json.get("type", 1) != 2:
            return

        for player in leaderboard_json.get("players", []):
            update_player(player, leaderboard, timestamp)


def update_player(player, leaderboard, timestamp):
    user_id = player["baseInfo"]["userid"]
    name = player["baseInfo"]["riskInfo"].get("name", "Unknown")
    rank = player.get("rank", 0)
    points = player.get("point", 0)
    power = player["fightPoint"].get("highestPoint", 0)
    total_wins = player["fightPoint"].get("totalWins", 0)

    record = PlayerRecord(
        id=user_id,
        timestamp=timestamp,
        metrics=MetricDataPoint(mmr=points, power=power, world_rank=rank, total_wins=total_wins),
        name=name
    )
    leaderboard.add_record(record)
