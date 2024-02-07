import util
import scrapper

if __name__ == "__main__":


    logging.basicConfig(level=logging.INFO)
    util.load_variables()


    sites = (
        "steam",
        "pc_gaming_wiki",
        "gamestatus"
    )

    for site in sites:
        scrapper.seek_and_destroy(site)



