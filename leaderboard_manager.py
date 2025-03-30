import settings
from log_importer import extract_leaderboard_data


def load_leaderboard():
    print("Loading existing leaderboard data...")
    leaderboard = settings.load_leaderboard()
    print("Importing new records from logs...")
    new_leaderboard = extract_leaderboard_data(settings.get_log_filepath())

    print("Merging data...")
    merge_leaderboards(new_leaderboard, leaderboard)

    print("Calculate metrics...")
    leaderboard.update_metrics()
    print(f"Leaderboard latest record is: {leaderboard.last_timestamp}")

    print("Saving updated leaderboard...")
    settings.save_leaderboard(leaderboard)

    return leaderboard


def merge_leaderboards(source, target):
    new_players = 0
    new_records = 0
    for player_id, source_player in source.players.items():
        if player_id in target.players:
            for source_record in source_player.records:
                if not any(target_record.timestamp == source_record.timestamp for target_record in
                           target.players[player_id].records):
                    target.players[player_id].add_record(source_record)
                    new_records = new_records + 1
        else:
            target.players[player_id] = source_player
            new_players = new_players + 1

    print(f"Discovered {new_records} new records!")
    print(f"Discovered {new_players} new players!")
