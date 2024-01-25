import os
import json
import apache_beam as beam
from datetime import datetime
from apache_beam.io.mongodbio import ReadFromMongoDB
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from dotenv import load_dotenv
load_dotenv()


CONNECTION_STRING_CLOUD = os.getenv('CONNECTION_STRING_CLOUD')
DB = os.getenv('DB')
CRACKLIST = os.getenv('CRACKLIST')
PC_GAMING_WIKI = os.getenv('PC_GAMING_WIKI')
STEAM = os.getenv('STEAM')


p = beam.Pipeline()

# Conector do banco de dados
mongo_uri = CONNECTION_STRING_CLOUD
db = DB
steam_collection = STEAM
game_details_collection = PC_GAMING_WIKI
cracks_collection = CRACKLIST

# Define a função para realizar a junção
def join_collections(element):
    key, elements = element
    steam_elements, game_details_elements, cracks_elements = elements['steam'], elements['game_details'], elements['cracks']
    
    for steam in steam_elements:
        for game_details in game_details_elements:
            for crack in cracks_elements:
                # Verifica se a chave 'name' é a mesma em todos os elementos
                if steam['name'] == game_details['name'] == crack['name']:
                    # Adiciona os campos das coleções `steam_appid` e `cracks` à coleção `game_details`
                    game_details.update(steam)
                    game_details.update(crack)
                    
                    # Remove campos indesejados
                    unwanted_fields = ['_id', 'Battlenet DRM', 'EA Desktop DRM', 'EA Play', 'EA Play Pro', 'EA Play Steam',
                                        'Epic Games Store DRM', 'Ubisoft Plus', 'Released', 'Released Windows',
                                        'Released__precision', 'Released Windows__precision']
                    for field in unwanted_fields:
                        game_details.pop(field, None)
                    
                    # Mover os campos 'name' e 'appid' para o início
                    game_details['name'], game_details['appid'] = game_details.pop('name'), game_details.pop('appid')

                    yield game_details

def convert_datetime_to_string(element):
    from datetime import datetime
    def convert_datetime(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d') 
        return obj

    def convert_element(obj):
        if isinstance(obj, dict):
            return {key: convert_element(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_element(item) for item in obj]
        else:
            return convert_datetime(obj)

    return convert_element(element)

def convert_to_json(element):
    return json.dumps(element)


def remove_duplicates(elements):
    import pandas as pd
    import json

    # Converte os elementos JSON para um DataFrame Pandas
    df = pd.DataFrame([json.loads(element) for element in elements])

    # Remove duplicatas com base nas colunas 'name' e 'appid'
    df_no_duplicates = df.drop_duplicates(subset=['name', 'appid'])

    # Converte o DataFrame de volta para a lista de dicionários
    result = df_no_duplicates.to_dict(orient='records')

    return result

# Leitura das coleções
colecao_steam = (
    p
    | 'ReadCollectionSteam' >> ReadFromMongoDB(uri=mongo_uri, db=db, coll=steam_collection, bucket_auto=True)
    | 'Mapping names from Steam' >> beam.Map(lambda record: (record["name"], record))
)

colecao_game_details = (
    p
    | 'ReadCollectionGameDetails' >> ReadFromMongoDB(uri=mongo_uri, db=db, coll=game_details_collection, bucket_auto=True)
    | 'Mapping names from Game Details' >> beam.Map(lambda record: (record["name"], record))
)

colecao_cracks = (
    p
    | 'ReadCollectionCracks' >> ReadFromMongoDB(uri=mongo_uri, db=db, coll=cracks_collection, bucket_auto=True)
    | 'Mapping names from Cracks' >> beam.Map(lambda record: (record["name"], record))
)

# Junção das coleções usando CoGroupByKey
joined_collections = ({'steam': colecao_steam, 'game_details': colecao_game_details, 'cracks': colecao_cracks}
                      | 'CoGroupByKey' >> beam.CoGroupByKey()
                      | 'JoinCollections' >> beam.FlatMap(join_collections)
                      )

joined_collections_str = (joined_collections
                         | 'ConvertDateTimeToString' >> beam.Map(convert_datetime_to_string))


joined_collections_json = (joined_collections_str
                           | 'ConvertToJSON' >> beam.Map(convert_to_json))

no_duplicates = (joined_collections_json
                 | 'RemoveDuplicates' >> beam.Map(remove_duplicates)
                 )

# Escrita dos resultados
no_duplicates | 'WriteResults' >> WriteToText('test', file_name_suffix='json')


# Execução do pipeline
p.run()