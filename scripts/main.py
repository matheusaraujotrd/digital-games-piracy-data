import util
import logging
import scrapper

# Setting up logs
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
    force=True
    )
logger = logging.getLogger("DCP")
sth = logging.StreamHandler()
sth.setFormatter(formatter)
sth.setLevel(logging.INFO)
logger.addHandler(sth)


# Load environment variables
variables = util.load_variables()

logger.info('Iniciando scraping das fontes')
scrapper.run(variables, logger, False, True, False)



