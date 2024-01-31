import dotenv

load_dotenv()

def load_variables():
    CONNECTION_STRING_CLOUD = os.getenv('CONNECTION_STRING_CLOUD')
    DB = os.getenv('DB')
    STEAM = os.getenv('STEAM')
    PC_GAMING_WIKI = os.getenv('PC_GAMING_WIKI')
    CRACKLIST = os.getenv('CRACKLIST')
    BUCKET = os.getenv('BUCKET')
    BUCKET_STAGING = os.getenv('BUCKET_STAGING')
    TEMPLATE_LOCATION = os.getenv('TEMPLATE_LOCATION')