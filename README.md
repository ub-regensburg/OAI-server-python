# Documentation

## Package Summary

This repository contains a **OpenAPI-Specification** for an **OAI-PMH** Interface.
It also contains:

* pydantic data models generated with the python-nextgen openapi-generator
* python method stubs for a **Flask** Webserver that can also be integrated into an existing server

## Instructions

### Generating data models from the specification

#### Requirements

* nodejs **version >= 12.22**
* npm **version >= 6.14**
* java JRE **version >= 11.0**

#### Steps

1. Install the openapi-generator-cli command

    ```bash
    npm install @openapitools/openapi-generator-cli -g
    ```
    
1. Use the openapi generator to generate python data models (based on [pydantic](https://docs.pydantic.dev/))

    ```bash
    sh generate.sh
    ```

1. The models will be put in the `oai_pmh/generated/models` directory

1. You can tweak the generator options found in `./oai_pmh/generator-config.json` to fit your use case

1. If you want to generate more than just the data models, remove the marked lines in the `./oai_pmh/.openapi-generator-ignore` file

### Building an OAI server with flask

#### Requirements

* Python **version >= 3.10**

#### Steps
1. Setup a Python Virtual Environment as described [here](https://docs.python.org/3/library/venv.html)

1. Install requirements

    1. Install global requirements for flask server

        ```bash
        pip install -r requirements.txt
        ```

    1. Install requirements for generated data models

        ```bash
        pip install -r oai_pmh/requirements.txt
        ```

1. Study the python files in `./oai_pmh`

    * `__init__.py` initializes a flask application

    * Files in the *routes* directory named after OAI verbs (e.g. `get_record.py`) contain a basic implementation for the corresponding method

    * `oai.py` contains the standard endpoint implementation

    * `shared.py` contains function stubs that return mock data.

1. Start the server in debug mode from the console

    ```bash
    flask --app oai_pmh run --debug
    ```

    This will start your server locally on port 5000

1. Post the following URL in your browser address bar to check if the server is running correctly

    [http://localhost:5000/default/oai?verb=Identify](http://localhost:5000/default/oai?verb=Identify)

    You should get the following response:

    ```xml
        <OAI-PMH xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
            <responseDate>2023-04-19</responseDate>
            <request verb="ListRecords">http://localhost:5000/oai</request>
            <Identify>
                <repositoryName>Test Repository</repositoryName>
                <baseURL>http://localhost:5000/oai</baseURL>
                <protocolVersion>2.0</protocolVersion>
                <adminEmail>sysadmin@example.de</adminEmail>
                <adminEmail>admin@example.de</adminEmail>
                <earliestDatestamp>1999-01-01</earliestDatestamp>
                <deletedRecord>transient</deletedRecord>
                <granularity>YYYY-MM-DD</granularity>
                <compression>gzip</compression>
                <compression>br</compression>
                <description>A OAI-PMH test server</description>
            </Identify>
        </OAI-PMH>
    ```


1. Now add a subfolder in the `plugin` directory.
Your oai endpoint will later use the folder name for routing.
E.g. If you add a subfolder named `myapi` your endpoint will later be [http://localhost:5000/myapi/oai](http://localhost:5000/myapi/oai)

1. In the subfolder add a python file with the name `convert.py`.
It will contain all the code you need to write, to publish your data on your OAI endpoint.

1. Implement the following functions in your `convert.py`.
Each of them corresponds with one of the OAI verbs, so for a complete endpoint they all need to be implemented:

    | OAI Verb | Function in convert.py |
    |-------|----------------------------|
    | Identify | create_identify(url) |
    | ListIdentifiers | create_identifiers(metadata_prefix, start_date, end_date, set) |
    | ListRecords | create_records(metadata_prefix, start_date, end_date, set) |
    | GetRecord | create_record(identifier, metadata_prefix) |
    | ListMetadataFormats | create_metadata_formats(identifier) |
    | ListSets | create_sets() |

1. Now your OAI endpoint should be complete.
Start the flask server and check all endpoints for correctly formatted data.