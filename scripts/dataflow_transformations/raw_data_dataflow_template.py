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
BUCKET_RAW = os.getenv('BUCKET_RAW')
BUCKET_STAGING_RAW = os.getenv('BUCKET_STAGING_RAW')
TEMPLATE_LOCATION_RAW = os.getenv('TEMPLATE_LOCATION_RAW')
SERVICE_ACCOUNT = os.getenv('SERVICE_ACCOUNT')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('SERVICE_ACCOUNT')


pipeline_options_dict = {
    'project': 'jogos-digitais-410204',
    'runner': 'DataflowRunner',
    'region': 'southamerica-east1',
    'staging_location': BUCKET_STAGING_RAW,
    'template_location': TEMPLATE_LOCATION_RAW,
}


pipeline_options = PipelineOptions.from_dictionary(pipeline_options_dict)
p = beam.Pipeline(options=pipeline_options)

# Conector do banco de dados
mongo_uri = CONNECTION_STRING_CLOUD
db = DB
steam_collection = STEAM
game_details_collection = PC_GAMING_WIKI
cracks_collection = CRACKLIST

# Define a função para realizar a junção
# Define a função para realizar a junção
def join_collections(element):
    key, elements = element
    steam_elements, game_details_elements, cracks_elements = elements['steam'], elements['game_details'], elements['cracks']

    for steam in steam_elements:
        for game_details in game_details_elements:
            for crack in cracks_elements:
                if steam['name'] == game_details['name'] == crack['name']:
                    # Combine the dictionaries
                    game_details.update(steam)
                    game_details.update(crack)

                    yield game_details

class ConvertToPandasDataFrame(beam.DoFn):
    def process(self, element):
        import pandas as pd
        # Convert the joined elements to a Pandas DataFrame
        df = pd.DataFrame([element])

        # Export the DataFrame to CSV
        csv_data = df.to_csv(index=False, line_terminator='\n').strip()

        # Yield the CSV data
        yield csv_data

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

joined_collections_pandas = (
    joined_collections
    | 'ConvertToPandasDataFrame' >> beam.ParDo(ConvertToPandasDataFrame())
)
# Escrita dos resultados
joined_collections_pandas | 'WriteCSV' >> WriteToText(f'{BUCKET_RAW}/output/output', file_name_suffix='.csv', shard_name_template='')


# Execução do pipeline
p.run()