def seek_and_destroy(url):
    client = MongoClient(CONNECTION_STRING_CLOUD)
    db = client[DB]
    collection = db[STEAM]

    if url == "steam":
        db.collection.deleteMany({})
        logging.info(collection.count_documents({}))
        if collection.count_documents({}) == 0:
            game_names = []
            game_names_standardized = []
            game_appids = []
            request = rq.get(f"https://api.steampowered.com/ISteamApps/GetAppList/v2/?access_token={STEAM_AK}")
            if response.status_code == 200:
                data = request.json()
                for item in data["applist"]["apps"]:
                    if item["name"] != None or item["name"] != "":
                        game_names.append(item["name"])
                        game_names_standardized.append(util.standardize_name(item["name"]))
                        game_appids.append(item["appid"])
                        logging.info(f"{item['appid']} - {item['name']} coletado!")
                    else:
                        logging.info(f"{item['appid']} não tem nome no banco de dados Steam...")
                game_labels = ("nome", "nome_pdr", "appid")
                games = zip(game_names, game_names_standardized, appids)
                games_doc = []

                for game in games:
                    game_dict = dict(zip(game_labels, game))
                    games_doc.append(game_dict)
                collection.insert_many(games_doc)
                logging.info("Dados inseridos no MongoDB!")
            else:
                logging.info("Falha em contatar a API steam...")


        client.close()
    elif url == "pc_gaming_wiki":
        pass
    elif url == "gamestatus":
        pass
