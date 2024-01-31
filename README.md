# Pirataria de Jogos Digitais

## Contexto
Este recurso foi criado durante uma iniciativa da **Dados de Fato** para uma apresentação a respeito da eficácia das travas antipirataria nos jogos de computador. Até a redação desta documentação, a análise não havia sido concluída ou publicada, mas decidi usar minha infraestrutura de dados como portfólio ainda assim.

## Visão Geral do Projeto
O projeto é um serviço de engenharia de dados do começo ao fim. A proposta é:
* Ingestão dos dados a partir de web scraping (usando Selenium, BeautifulSoup e técnicas de regex)
* Armazenação dos dados semiestruturados em um cluster do MongoDB (via Atlas Cloud)
  * Algumas transformações simples acontecem durante esta etapa, por isso esse projeto pode ser visto como um modelo de ETL (mas não só)
* Os dados semiestruturados são transformados por meio do Dataflow com Apache Beam
  * Aqui é onde ocorre a maior parte das transformações, fazendo deste um modelo majoritariamente ELT (ou um híbrido ETLT)
* Os dados são enviados do Dataflow até um bucket no Google Cloud Storage, já em formato csv.
* Esses dados são transformados uma última vez e enviados ao Big Query, inseridos em um Data Warehouse.

Dessa forma, temos uma infraestrutura de Data Lakehouse realizada do zero e do começo ao fim, usando **Selenium, Beautifulsoup, MongoDB e Google Cloud Platform (Dataflow, Cloud Storage e Big Query)**

## Dependências
Para conferir detalhes acerca das dependências do projeto, confira o [arquivo de dependências](pyproject.toml).

## Última atualização
Sempre que o projeto sofrer alguma atualização significativa, incluirei uma descrição aqui, bem como no restante da documentação, conforme for necessário.
* 30/01/2024 - Início da documentação, padronização da estrutura dos arquivos e refatoração do código.

## Licença
[Uso livre com atribuição](LICENSE.md).