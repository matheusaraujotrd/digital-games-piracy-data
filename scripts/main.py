from util import load_variables
import scrapper

# Setting up logs
logging.getLogger('DGP')
logging_config = logging.basicConfig(
    filename ="../logs.txt",
    level=logging.INFO
    )

# Load environment variables
variables = load_variables()

logging.info(f'Iniciando scraping das fontes')
scrapper.run(variables, logging_config)



