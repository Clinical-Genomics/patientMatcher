# patientMatcher
[![Build Status](https://travis-ci.com/Clinical-Genomics/patientMatcher.svg?branch=master)](https://travis-ci.com/Clinical-Genomics/patientMatcher) [![codecov](https://codecov.io/gh/Clinical-Genomics/patientMatcher/branch/master/graph/badge.svg?token=WXHDu9U8qk)](https://codecov.io/gh/Clinical-Genomics/patientMatcher)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5482517.svg)](https://doi.org/10.5281/zenodo.5482517)


Table of Contents:
1. [ Running the app using Docker ](#docker)
2. [ Installing the app on a virtual environment with a running instance of MongoDB ](#installation)
3. [ Data types ](#data_types)
4. [ Command line interface](#cli)
    - [ Adding demo data to server](#cli_add_demo)
    - [ Removing a patient from database ](#cli_remove_patient)
    - [ Adding a client to database ](#cli_add_client)
    - [ Adding a new connected node to database ](#cli_add_node)
5. [ Server endpoints ](#endpoints)
    - [ Add patient to server (/patient/add) ](#add)
    - [ Delete patient from server (/patient/delete/<patient_id>) ](#delete)
    - [ Get server stats (/metrics) ](#metrics)
    - [ Get the list of connected nodes (/nodes) ](#node_list)
    - [ Send a match request to server (/match) ](#match)
    - [ Send a match request to external nodes (/match/external/<patient_id>) ](#match_external)
    - [ Show all matches for a given patient (/matches/<patient_id>) ](#patient_matches)
6. [ Patient matching algorithm ](#matching_algorithm)
    - [ Genotyping matching algorithm ](#geno_matching)
    - [ Phenotyping matching algorithm ](#pheno_matching)
7. [ Enabling matching notifications ](#notify)
8. [ Enabling log errors notifications ](#log_errors)

<a name="docker"></a>
## Running the app using Docker
An example containing a demo setup for the app is included in the docker-compose file. Note that this file is not intended for use in production and is onpy provided to illustrate how the backend and frontend of the app could be connected to a mongodb instance stored on an external image. Start the docker-compose demo using this command:

```
docker-compose up -d
```
The command will create 3 containers:
- mongodb: starting a mongodb server with support for user authentication (--auth option)
- pmatcher-cli: the a command-line app, which will connect to the server and populates it with demo data
- pmatcher-web: a web server running on localhost and port 9020.

The server will be running and accepting requests sent from outside the containers (another terminal or a web browser). Read further down to find out about requests and commands.

To test server responses try to invoke the `metrics` endpoint with the following command:
```
curl localhost:5000/metrics
```

To stop the containers (and the server), run:
```
docker-compose down
```
Make sure that there are no mongo containers running before before running the command again.
Commands:
```
docker ps -a
docker rm <id of the eventual vepo/mongo container>
```

<a name="installation"></a>
## Installing the app on a virtual environment with a running instance of MongoDB

### Prerequisites
To use this server you'll need to have a working instance of **MongoDB**. from the mongo shell you can create a database and an authenticated user to handle connections using this syntax:

```bash
use pmatcher
db.createUser(
   {
     user: "pmUser",
     pwd: "pmPassword",
     roles: [ "dbOwner" ]
   }
)
```
After setting up the restricted access to the server you'll just have to launch the mongo demon using authentication:
```bash
mongod --auth --dbpath path_to_database_data
```

Clone patientMatcher repository from github using this command:

```bash
git clone https://github.com/Clinical-Genomics/patientMatcher.git
```

Change directory to the cloned folder and from there install the software using the following command:
```bash
pip install -r requirements.txt
pip install -e .
```

To customize the server configuration you'll need to edit the **config.py** file under the /instance folder. &nbsp;
For testing purposes you can keep the default configuration values as they are, but keep in mind that you should adjust these numbers when in production.

To start the server run this command:
```bash
pmatcher run -h custom_host -p custom_port
```
Please note that the code is NOT guaranteed to be bug-free and it must be adapted to be used in production.


<a name="data_types"></a>
## Data types
This server implements the [Matchmaker Exchange APIs](https://github.com/ga4gh/mme-apis). It accepts and returns patient data validated against the [json schema](https://github.com/MatchmakerExchange/reference-server/blob/master/mme_server/schemas/api.json) defined in the [MME reference-server project](https://github.com/MatchmakerExchange/reference-server).

&nbsp;&nbsp;

<a name="cli"></a>
## Command line interface
A list of available commands can be invoked by running the following command:
```bash
pmatcher
```
&nbsp;&nbsp;

<a name="cli_add_demo"></a>
### Adding demo data to server
For testing purposes you can upload a list of [50 benchmarking patients](https://github.com/ga4gh/mme-apis/tree/master/testing).&nbsp;
To add these patients to the database run the following command:
```bash
pmatcher add demodata --ensembl_genes
```
Please note that the list of benchmarking patients all gene ids are represented as HGNC gene symbols.
The command above, with the `--ensembl_genes` option, will convert gene symbols to Ensembl ids, in accordance to the GA4GH API: https://github.com/ga4gh/mme-apis/blob/master/search-api.md.

The above command will also load a demo client with token `DEMO` into the database
&nbsp;&nbsp;

<a name="cli_remove_patient"></a>
### Removing a patient from the database.
You can remove a patient using the command line interface by invoking this command and providing **either its ID or its label** (or both actually):

```bash
pmatcher remove patient [OPTIONS]

Options:
-id TEXT     ID of the patient to be removed from database
-label TEXT  label of the patient to be removed from database
```
&nbsp;&nbsp;

<a name="cli_add_client"></a>
### Adding a client to the database
In order to save patients into patientMatcher you need to create at least one authorized client.&nbsp;
Use the following command to insert a client object in the database:

```bash
pmatcher add client [OPTIONS]

Options:
-id TEXT       Client ID  [required]
-token TEXT    Authorization token  [required]
-url TEXT      Client URL  [required]
-contact TEXT  Client email
```
POST request aimed at adding or modifying a patient in patientMatcher **should be using a token** from a client present in the database.&nbsp;
Clients may be from the command line with this command:
```bash
pmatcher remove client -id client_id
```
&nbsp;&nbsp;

<a name="cli_add_node"></a>
### Adding a connected node to the database
To connect to another MME node and submit requests to it you should know the authentication token to the other node.&nbsp;
You can add a node to the database by running the command:

```bash
pmatcher add node [OPTIONS]

Options:
  -id TEXT                Server/Client ID  [required]
  -token TEXT             Authorization token  [required]
  -matching_url TEXT      URL to send match requests to  [required]
  -accepted_content TEXT  Accepted Content-Type  [required]
  -contact TEXT           An email address
```
Connected nodes may be removed any time using the command:&nbsp;
```bash
pmatcher remove node -id node_id
```
&nbsp;&nbsp;

<a name="endpoints"></a>
## Server endpoints

<a name="add"></a>
- **/patient/add**.
&nbsp;To add patients using a **POST** request. Example:
```bash
curl -X POST \
  -H 'X-Auth-Token: DEMO' \
  -H 'Content-Type: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -H 'Accept: application/json' \
  -d '{"patient":{
    "id":"patient_id",
    "contact": {"name":"Contact Name", "href":"mailto:contact_name@mail.com"},
    "features":[{"id":"HP:0009623"}],
    "genomicFeatures":[{"gene":{"id":"EFTUD2"}}]
  }}' localhost:9020/patient/add
```
To update the data of a patient already submitted to the server you can use the same command and add a patient with the same ID.&nbsp;

The action of adding or updating a patient in the server will trigger an **external search of similar patients from connected nodes**.&nbsp;
If there are no connected nodes in the database or you are uploading demo data no search will be performed on other nodes.

&nbsp;&nbsp;

<a name="delete"></a>
- **patient/delete/<patient_id>**.
&nbsp;You can delete a patient from the database by sending a **DELETE** request with its ID to the server. Example:
```bash
curl -X DELETE \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/patient/delete/patient_id
```
Please note that when a patient is deleted all its match results will be also deleted from the database. This is valid for **matches where the patient was used as the query patient** in searches performed on other nodes or the internal patientMatcher database (internal search).
Matching results where the removed patient is instead listed among the matching results will be not removed from the database.

&nbsp;&nbsp;

<a name="metrics"></a>
- **/metrics**.
&nbsp;Use this endpoint to **get** database metrics.<br>
Stats which could be retrieved by a MME service are described [here](https://github.com/ga4gh/mme-apis/blob/master/metrics-api.md)<br>
Example:
```bash
curl -X GET \
  localhost:9020/metrics
```
&nbsp;&nbsp;

<a name="node_list"></a>
- **/nodes**.
&nbsp;**GET** the list of connected nodes. Example:
```bash
curl -X GET \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/nodes
```
The response will return a list like this : [ { 'id' : node_1_id, 'description' : node1_description }, .. ] or an empty list if the server is not connected to external nodes.

&nbsp;&nbsp;

<a name="match"></a>
- **/match**.
&nbsp;**POST** a request with a query patient to patientMatcher and get a response with the patients in the server which are most similar to your query. Example:
```bash
curl -X POST \
  -H 'X-Auth-Token: DEMO' \
  -H 'Content-Type: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -H 'Accept: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -d '{"patient":{
    "id":"patient_id",
    "contact": {"name":"Contact Name", "href":"mailto:contact_name@mail.com"},
    "features":[{"id":"HP:0009623"}],
    "genomicFeatures":[{"gene":{"id":"EFTUD2"}}]
  }}' localhost:9020/match
```
The **maximum number of patients returned by the server** is a parameter which can be customized by editing the "MAX_RESULTS" field in the config.py file. Default value is 5.
Patient matches are returned in order or descending similarity with the query patient (The most similar patients are higher in the list of results).

Another customizable parameter is the minimum patient score threshold for returned results (**SCORE_THRESHOLD** in the config file). Matches with patient score lower than this number won't be returned. Default value for this parameter is 0.

&nbsp;&nbsp;
<a name="match_external"></a>
- **/match/external/<patient_id>**.
&nbsp;Trigger a search in external nodes for patients similar to the one specified by the ID. Example:
```bash
curl -X POST \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/match/external/patient_id
```
It is possible to search for matching patients on a specific node. To do so specify the node id in the request args. Example:
```bash
curl -X POST \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/match/external/patient_id?node=specific_node_id
```
Read [here](#node_list) how to get a list with the ID of the connected nodes.

&nbsp;&nbsp;

<a name="patient_matches"></a>
- **/matches/<patient_id>**.
&nbsp;Return all matches (internal and external) with positive results for a patient specified by an ID. Example:
```bash
curl -X GET \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/matches/patient_id
```
&nbsp;&nbsp;

<a name="matching_algorithm"></a>
## Patient matching algorithm.
Each patient query submitted to the server triggers a matching algorithm which will search and return those patients on the server that are most similar to the queried one.
Patient similarity is measured by the a **similarity score** that may span **from 0 (no matching) to 1 (exact matching)**.

Similarity score computation is taking into account **genomic similarity** and **phenotype similarity** across patients. The weight of these two factors is numerically evaluated into a GTscore and a PhenoScore, and the sum of the 2 constitutes the similarity score of the matching patient.

The relative weight of the GTscore and the PhenoScore can be customised by the database administrator by changing the values of the parameters "MAX_GT_SCORE" and "MAX_PHENO_SCORE" in the configuration file (instance/config.py). Default values are MAX_GT_SCORE: 0.5, MAX_PHENO_SCORE : 0.5.

<a name="geno_matching"></a>
### Genotyping matching algorithm
GTscore is computed by evaluating the list of genomic features of the queried patient and the patients available on the MME server. **PatientMatcher patients are saved with gene ids described by Ensembl gene ids**, but it's possible to search the database using patients with genes represented by HGNC symbols, Entrez ids and Ensembl ids.

If the queried patient has no genomic features (only phenotype features) then GTscore of all the returned matches will be 0.

Example of how the algorithm works:
Let's assume that 0.5 is the MAX_GT_SCORE possible for a patient match (default parameters).

If for instance the queried patient (QUERY) has 3 variants, **each variant will have a relative weight** of 0.1666 (0.5/3). 0.1666 will be the maximum score for each variant.
Assuming having a QUERY patient with these variants:
 - gene X variant A
 - gene Y variant B
 - gene Z variant C

Any patient in the database having variants in any of the X,Y,Z genes will constitute a match (MATCH) to the queried patient and will be compared against it.
Let's assume the variants in MATCH are:
- gene X variant D (1)
- gene Y variant B (2)
- gene W variant E (3)

The evaluation of the matching features is always performed on the QUERY variants, in this way:
- gene X variant A ---> gene match with (1). No variant match. Assigned score: 0.1666/4 (gene match only will be arbitrarily assigned a fourth of the relative weight of the variant)
- gene Y variant B ---> exact matching of variant and gene with (2). Assigned score: 0.1666 (max relative weight of the variant)
- gene Z variant C ---> No match, assigned score: 0.

GTscore assigned to the MATCH patients will then be: 0.1666/4 + 0.1666 + 0.

Note that the algorithm will evaluate and assign a score of 0.1666 (max relative weight of the variant) also to matching variants outside genes.
This way patients will be evaluated for genetic similarity even if the variants lay outside genes.


<a name="pheno_matching"></a>
### Phenotype matching algorithm
Phenotype similarity is calculated by taking into account **features and disorders** of a patient.

- **Patient features**
are specified by the eventual HPO terms provided for the query patient. **Similarity between HPO features will be equal the maximum similarity score** between two patients **if no disorders (OMIM terms) are provided** for one or both patients.   
**Otherwise feature similarity score will make up 1/2 of the maximum similarity score**.
Feature similarity is calculated as the simgic score obtained by comparing HPO terms of a query patient with those from a matching patient.
You can find more information on semantic similarity comparison algorithms in [this paper](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-S5-S4)

- **Disorders**
(OMIM diagnoses), if available, will make up **1/2 of the maximum similarity score**. OMIM score is calculated by pairwise comparison of the available OMIM terms for the patients.
&nbsp;

<a name="notify"></a>
## Enabling match notifications

Email notification of patient matching can be enabled by editing the email notification parameters
in the configuration file (config.py). If you want to test your email configuration without sending real match notifications you could use this command:

```bash
pmatcher test email -recipient your_email@email.com
```

It is possible to choose to send complete or partial info for matching patients in the email notification body. Set **NOTIFY_COMPLETE** to True (in config.py) if you want to notify complete patient data (i.e. variants and phenotypes will be shared by email) or set it to False if email body should contain ONLY contact info and patient IDs for all matching patients. This latter option is useful to better secure the access to sensitive data.<br>

Once these parameters are set to valid values a notification email will be sent in the following cases:

 - A patient is added to the database and the add request triggers a search on external nodes. There is at least one returned result (/patient/add endpoint).
 - An external search is actively performed on connected nodes and returns at least one result (/match/external/<patient_id> endpoint).
 - The server is interrogated by an external node and returns at least one match (/match endpoint). In this case a match notification is sent to each contact of the matches (patients in results).
 - An internal search is submitted to the server using a patient from the database (/match endpoint) and this search returns at least one match. In this case contact users of all patients involved will be notified (contact from query patient and contacts from the result list of patients).

 You can stop server notification any time by commenting the MAIL_SERVER parameter in config file and rebooting the server.


<a name="log_errors"></a>
## Enabling log errors notifications
App email notifications might be enabled by providing one or more email addresses as values for the ADMINS parameter in the configuration file. Note that the email handler will only notify app errors (LOG level = error).



[travis-url]: https://travis-ci.org/Clinical-Genomics/patientMatcher
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/patientMatcher.svg?style=flat-square
