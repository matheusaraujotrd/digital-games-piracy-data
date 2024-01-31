import requests as rq
from dotenv import load_dotenv
import os
load_dotenv()

STEAM_KEY = os.getenv('STEAM_KEY')
STEAM_AK = os.getenv('STEAM_AK')

def api(mode):
    appid = []
    if mode == 'mp':
        request = rq.get(f"https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/?key={STEAM_KEY}")
        data = request.json()
        appid = [item["appid"] for item in data["response"]["ranks"]]
    return appid


def get_names(appid):
    game_names = []
    request = rq.get(f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?access_token={STEAM_AK}")
    data = request.json()
    for id in appid:
        for item in data["applist"]["apps"]:
            if id == item["appid"]:
                game_names.append(item["name"])
    return game_names

def write_to_file(game_names, path, name):
    if os.path.exists(path):
        os.remove(path)

    with open(name,"w+", encoding="utf-8") as f:
        for game in game_names:
            f.write(f"{game}\n")

def main():
    pass 

if __name__ == "__main__":
    mode = 0
    mode = int(input("Desired mode:\n0 - quit\n1 - Most Played\n2 - appid most played mode"))
    if mode == 0:
        pass
    elif mode == 1:
        appid = api('mp')
        game_names = get_names(appid)
        write_to_file(game_names, "/steam_most_played.txt", "steam_most_played.txt")
    elif mode == 2:
        appid = api('mp')
        write_to_file(appid, "/steam_appids_most_played.txt", "steam_appids_most_played.txt")