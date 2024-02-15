# Pirataria de Jogos Digitais [PT-BR]

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

* 15/02/2024 - Correção de bugs. [<u>*version 0.2.1*</u>]
* 14/02/2024 - Primeira refatoração do código concluída. Pipeline completa até a aquisição final de dados.<br>A próxima etapa é a refatoração da transformação via Dataflow e posterior armazenamento de dados.<br>A proposta final é um consumo menor do Dataflow e, dessa forma, economizar gastos. [<u>*versão 0.2.0*</u>]
* 09/02/2024 - Refatoração de 66% do código original [<u>*versão 0.1.5*</u>]
* 30/01/2024 - Início da documentação, padronização da estrutura dos arquivos e refatoração do código. [<u>*versão 0.1.0*</u>]

## Licença
[Uso livre com atribuição](LICENSE.md).

<br><br><br><br>
# Digital Game Piracy [EN]
## Context
This resource was created during an initiative by **Dados de Fato** for a presentation on the effectiveness of anti-piracy measures in computer games. As of the writing of this documentation, the analysis had not been completed or published, but I decided to use my data infrastructure as a portfolio nonetheless.

## Project Overview
The project is an end-to-end data engineering service. The proposal includes:

* Data ingestion through web scraping (using Selenium, BeautifulSoup, and regex techniques)
* Storage of semi-structured data in a MongoDB cluster (via Atlas Cloud)
  * Some simple transformations occur during this stage, so this project can be seen as an ETL model (but not only)
* Semi-structured data is transformed through Dataflow with Apache Beam
  * This is where most of the transformations take place, making it mostly an ELT model (or a hybrid ETLT)
* Data is sent from Dataflow to a bucket in Google Cloud Storage, already in csv format.
* This data is transformed one last time and sent to Big Query, inserted into a Data Warehouse.

Thus, we have a Data Lakehouse infrastructure done from scratch and end-to-end, using **Selenium, BeautifulSoup, MongoDB, and Google Cloud Platform (Dataflow, Cloud Storage, and Big Query)**.

## Dependencies
To check details about the project dependencies, refer to the [dependencies file](pyproject.toml).

## Last Update
Whenever the project undergoes a significant update, I will include a description here, as well as in the rest of the documentation as needed.

* 15/02/2024 - Minor bug fixes. [<u>*version 0.2.1*</u>]
* 14/02/2024 - First code refactoring completed. Full pipeline up to the final data acquisition ready.<br>The next step is the refactoring of the transformation via Dataflow and subsequent data storage.<br>The final goal is to reduce Dataflow consumption and, thus, save costs. [<u>*version 0.2.0*</u>]
* 09/02/2024 - Refactoring of 66% of the original code [<u>version 0.1.5</u>]
* 30/01/2024 - Start of documentation, standardization of file structure, and code refactoring. [<u>version 0.1.0</u>]

## License
[Free to use with attribution](LICENSE.md).