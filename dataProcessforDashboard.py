import pandas as pd
import datetime
import os

# Generate URLs for different match types
listofATP = [f"https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_{i}.csv" for i in range(1968, 2025)]
listofDTP = [f"https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_doubles_{i}.csv" for i in range(2000, 2020)]
listofFutures = [f"https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_futures_{i}.csv" for i in range(1991, 2025)]
listofQuallChall = [f"https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_qual_chall_{i}.csv" for i in range(1978, 2025)]


def load_csv_files(url_list):
    """ Load and concatenate CSV files from a list of URLs """
    try:
        return pd.concat([pd.read_csv(url) for url in url_list], ignore_index=True)
    except Exception as e:
        print(f"Error loading CSV files: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on failure


def transform_date(x):
    """ Convert integer date format YYYYMMDD to datetime """
    try:
        return pd.to_datetime(str(x), format='%Y%m%d')
    except (ValueError, TypeError):
        return pd.NaT  # Return NaT if conversion fails


def update_data():
    """ Update data by downloading and processing all match data """
    solo = load_csv_files(listofATP)
    solo["matchType"] = "solo"
    
    double = load_csv_files(listofDTP)
    double["matchType"] = "double"
    
    futures = load_csv_files(listofFutures)
    futures["matchType"] = "futures"
    
    quall_chall = load_csv_files(listofQuallChall)
    quall_chall["matchType"] = "Qualification Challenge"
    
    final_df = pd.concat([solo, futures, quall_chall], ignore_index=True)
    final_df["date"] = final_df["tourney_date"].apply(transform_date)
    
    final_df.to_csv("rawData.csv", index=False)


def clean_data(final_df):
    """ Clean and process the raw match data """
    player = pd.read_csv("https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_players.csv")
    current_rank = pd.read_csv("https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_rankings_current.csv")

    player["dob"] = player["dob"].apply(transform_date)
    current_rank["ranking_date"] = current_rank["ranking_date"].apply(transform_date)
    
    player["player_id"] = player["player_id"].astype(str)
    current_rank["player"] = current_rank["player"].astype(str)

    basic_info_cols = ["tourney_id", "tourney_name", "surface", "matchType", "tourney_level", "date"]

    # Create winner and loser datasets
    winner_cols = [col for col in final_df.columns if "winner" in col or "w_" in col] + basic_info_cols
    loser_cols = [col for col in final_df.columns if "loser" in col or "l_" in col] + basic_info_cols
    
    winner_df = final_df[winner_cols].copy()
    loser_df = final_df[loser_cols].copy()
    
    winner_df["issue"] = "win"
    loser_df["issue"] = "lost"
    
    # Standardize column names
    winner_df.columns = [col.replace("winner", "player").replace("w_", "p_") for col in winner_df.columns]
    loser_df.columns = [col.replace("loser", "player").replace("l_", "p_") for col in loser_df.columns]
    
    all_matches_df = pd.concat([winner_df, loser_df], ignore_index=True)
    all_matches_df["player_id"] = all_matches_df["player_id"].astype(str)

    # Aggregate statistics
    win_loss_stats = all_matches_df.groupby(["player_id", "issue"]).size().unstack(fill_value=0).reset_index()
    win_loss_stats.columns = ["player_id", "allLost", "allWin"]
    
    player = player.merge(win_loss_stats, on="player_id", how="left")
    player["player"] = player["name_first"] + " " + player["name_last"]
    
    highest_rank = all_matches_df.groupby("player_id")["player_rank"].min().reset_index().rename(columns={"player_rank": "highestRank"})
    player = player.merge(highest_rank, on="player_id", how="left")

    # Save JSONs
    save_to_json(current_rank.rename(columns={"player": "player_id", "rank": "currentRank"}), "jsonData/currentRank.json")
    
    last_rank = get_last_rank(all_matches_df, current_rank)
    save_to_json(last_rank, "jsonData/playerRank.json")
    
    save_to_json(player, "jsonData/playerInfo.json")
    save_to_json(get_trophy_stats(final_df), "jsonData/Trophee.json")
    save_to_json(get_surface_stats(all_matches_df), "jsonData/surface.json")
    save_to_json(get_losing_stats(final_df), "jsonData/loser.json")
    save_to_json(get_player_stats(all_matches_df), "jsonData/PlayerStats.json")

    # Export to CSVs
    export_json_to_csv("jsonData")
    
    return all_matches_df, player


def save_to_json(df, filepath):
    """ Save DataFrame to JSON """
    df.to_json(filepath, orient="records")


def get_last_rank(all_matches_df, current_rank):
    """ Retrieve the last known rank of each player """
    last_rank = current_rank.sort_values(["player", "ranking_date"], ascending=[True, False])\
                            .drop_duplicates(subset="player", keep="first")\
                            .sort_values(by="rank")
    
    missing_players = set(all_matches_df["player_id"].unique()) - set(last_rank["player"].unique())
    
    last_rank_info = all_matches_df.loc[all_matches_df["player_id"].isin(missing_players)]\
                                  .sort_values("date", ascending=False)\
                                  .drop_duplicates(subset="player_id")\
                                  [["player_id", "player_rank", "date", "player_rank_points"]]\
                                  .rename(columns={"player_id": "player", "date": "ranking_date", "player_rank": "rank", "player_rank_points": "points"})
    
    return pd.concat([last_rank_info, last_rank])


def get_trophy_stats(final_df):
    """ Calculate trophy stats for each player """
    return final_df.loc[final_df["matchType"] == "solo"]\
                   .sort_values(["tourney_id", "match_num"], ascending=[True, False])\
                   .drop_duplicates(subset=["tourney_id"])\
                   .groupby(["winner_id", "tourney_level"])\
                   .size().reset_index(name="numberOfTrophee")\
                   .rename(columns={"tourney_level": "tourneyLevel"})


def get_surface_stats(all_matches_df):
    """ Calculate win/loss stats based on surface """
    return all_matches_df.groupby(["player_id", "surface", "issue"]).size().reset_index(name="winMatch")


def get_losing_stats(final_df):
    """ Calculate losing stats for each player """
    loser_stats = final_df.groupby(["loser_id", "winner_name"]).size().reset_index(name="timeLosing")
    loser_stats['issue'] = "lost"
    
    winner_stats = final_df.groupby(['winner_id', 'loser_name']).size().reset_index(name='timeLosing')\
                           .rename(columns={"winner_id": "loser_id", "loser_name": "winner_name"})
    winner_stats['issue'] = "win"
    
    return pd.concat([loser_stats, winner_stats])


def get_player_stats(all_matches_df):
    """ Calculate player serve and game statistics """
    all_matches_df["first_serve_percentage"] = all_matches_df["p_1stIn"] / all_matches_df["p_svpt"]
    all_matches_df["first_serve_points_won_percentage"] = all_matches_df["p_1stWon"] / all_matches_df["p_1stIn"]
    all_matches_df["second_serve_points_won_percentage"] = all_matches_df["p_2ndWon"] / (all_matches_df["p_svpt"] - all_matches_df["p_1stIn"])
    all_matches_df["break_points_saved_percentage"] = all_matches_df["p_bpSaved"] / all_matches_df["p_bpFaced"]
    
    serve_stats = all_matches_df.groupby("player_id").agg({
        "first_serve_percentage": "mean",
        "first_serve_points_won_percentage": "mean",
        "second_serve_points_won_percentage": "mean",
        "break_points_saved_percentage": "mean",
        "p_ace": "mean",
        "p_df": "mean"
    }).reset_index().fillna(0).rename(columns={"p_ace": "number_of_aces", "p_df": "number_of_double_faults"})
    
    return serve_stats


def export_json_to_csv(directory):
    """ Export all JSON files in a directory to CSV """
    json_files = [f for f in os.listdir(directory) if f.endswith(".json")]
    for file in json_files:
        df = pd.read_json(os.path.join(directory, file))
        csv_filename = file.replace(".json", ".csv")
        df.to_csv(f"Tableau/{csv_filename}", index=False)


# Usage
update_data()  # Update raw data
final_df = pd.read_csv("rawData.csv")  # Load raw data
all_matches_df, player_df = clean_data(final_df)  # Clean and process data
