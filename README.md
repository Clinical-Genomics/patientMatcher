# patientMatcher
[![Build Status](https://travis-ci.com/northwestwitch/patientMatcher.svg?branch=master)](https://travis-ci.com/northwestwitch/patientMatcher) [![Coverage Status](https://coveralls.io/repos/github/Clinical-Genomics/patientMatcher/badge.svg?branch=master&kill_cache=1)](https://coveralls.io/github/Clinical-Genomics/patientMatcher?branch=master)

## Prerequisites
To use this server you'll need to have a working instance of MongoDB. from the mongo shell you can create a database and an authenticated user to handle connections using this syntax:

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

## Installation
Clone the repository from github using this command:
```bash
git clone https://github.com/Clinical-Genomics/patientMatcher.git
```

To customize the server configuration you'll need to edit the **config.py** file under the /instance folder. For testing purposes you can keep the default configuration values as they are, but be sure no to use these values in production!

Change directory to the cloned folder and from there install the software using the following command:
```bash
pip install -e .
```

To run the application server you can execute the following command:
```bash
python run.py
```

## Command line interface
A list of available commands can be invoked by running the following command:
```bash
pmatcher
```

### Adding demo data to server
For testing purposes you can upload a list of [50 benchmarking patients](https://github.com/ga4gh/mme-apis/tree/master/testing).
To add these patients to the database run the following command:
```bash
pmatcher add demodata
```

### Adding a connected node to the database
To connect to another MME node and submit requests to it you should know the authentication token to the other node.
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

### Adding a client to the database
In order to save patients into patientMatcher you need to create at least one authorized client.
Use the following command to insert a client object in the database:

```bash
pmatcher add client [OPTIONS]

Options:
-id TEXT       Client ID  [required]
-token TEXT    Authorization token  [required]
-url TEXT      Client URL  [required]
-contact TEXT  Client email
```
POST request aimed at adding or modifying a patient in patientMatcher **should be using a token** from a client present in the database.


### Removing a patient from the database.
You can remove a patient using the command line interface by invoking this command and providing **either its ID or its label** (or both actually):

```bash
pmatcher remove patient [OPTIONS]

Options:
-id TEXT     ID of the patient to be removed from database
-label TEXT  label of the patient to be removed from database
```

## Server endpoints

- **/patient/add**
To add patients using a **POST** request. Example:
```bash
curl -X POST \
  -H 'X-Auth-Token: custom_token' \
  -H 'Content-Type: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -H 'Accept: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -d '{"patient":{
    "id":"patient_id",
    "contact": {"name":"Jane Doe", "href":"mailto:jdoe@example.edu"},
    "features":[{"id":"HP:0009623"}],
    "genomicFeatures":[{"gene":{"id":"EFTUD2"}}],
    "test": true
  }}' localhost:9020/patient/add
```

To update the data of a patient already submitted to the server you can use the same command and add a patient with the same ID.

The action of adding or updating a patient in the server will trigger an **external search of similar patients from connected nodes**.
If there are no connected nodes in the database or you are uploading demo data no search will be performed on other nodes.


- **patient/delete/<patient_id>**
You can delete a patient from the database by sending a **DELETE** request with its ID to the server. Example:
```bash
curl -X DELETE \
  -H 'X-Auth-Token: custom_token' \
  -H 'Content-Type: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -H 'Accept: application/vnd.ga4gh.matchmaker.v1.0+json' \
  localhost:9020/patient/delete/patient_id
```

- **/patient/view**
Use this endpoint to **get** a list of all patients in the database. Example:
```bash
curl -X GET \
  -H 'X-Auth-Token: custom_token' \
  -H 'Content-Type: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -H 'Accept: application/vnd.ga4gh.matchmaker.v1.0+json' \
  localhost:9020/patient/view
```

- **/match**
**POST** a request with a query patient to patientMatcher and get a response with the patients in the server which are most similar to your query. Example:
```bash
curl -X POST \
  -H 'X-Auth-Token: custom_token' \
  -H 'Content-Type: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -H 'Accept: application/vnd.ga4gh.matchmaker.v1.0+json' \
  -d '{"patient":{
    "id":"patient_id",
    "contact": {"name":"Jane Doe", "href":"mailto:jdoe@example.edu"},
    "features":[{"id":"HP:0010943"}],
    "genomicFeatures":[{"gene":{"id":"EFTUD2"}}],
    "test": true
  }}' localhost:9020/match
```

- **/match/external/<patient_id>**
Trigger a search in external nodes for patients similar to the one specified by the ID.
In progress!!

- **/patient/matches/<patient_id>**
Return all matches found on external nodes for a patient specified by an ID
In progress!!


## Patient matching algorithm, used both for internal and external searches
Each patient query submitted to the server triggers a matching algorithm which will search and return those patients on the server that are most similar to the queried one.
Patient similarity is measured by the a **similarity score** that may span **from 0 (no matching) to 1 (exact matching)**.

Similarity score computation is taking into account **genomic similarity** and **phenotype similarity** across patients. The weight of these two factors is numerically evaluated into a GTscore and a PhenoScore, and the sum of the 2 constitutes the similarity score of the matching patient.

The relative weight of the GTscore and the PhenoScore can be customised by the database administrator by changing the values of the parameters "MAX_GT_SCORE" and "MAX_PHENO_SCORE" in the configuration file (instance/config.py). Default values are MAX_GT_SCORE: 0.5, MAX_PHENO_SCORE : 0.5.


### Genotyping matching algorithm
GTscore is computed by evaluating the list of genomic features of the queried patient and the patients available on the MME server.

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
- gene X variant A ---> gene match with (1). No variant match. Assigned score: 0.5/4 (gene match only will be arbitrarily assigned a fourth of the relative weight of the variant)
- gene Y variant B ---> exact matching of variant and gene with (2). Assigned score: 0.1666 (max relative weight of the variant)
- gene Z variant C ---> No match, assigned score: 0.

GTscore assigned to the MATCH patients will then be: 0.5/4 + 0.1666 + 0.

Note that the algorithm will evaluate and assign a score of 0.1666 (max relative weight of the variant) also to matching variants outside genes.
This way patients will be evaluated for genetic similarity even if the variants lay outside genes.


### Phenotype matching algorithm
Phenotype similarity is calculated by taking into account **features, disorders and computed phenotypes** of a patient

- **Patient features**
Are specifies by the eventual HPO terms provided for the query patient. **Similarity between HPO features will make up half of the maximum similarity score** between two patients.

- **Monarch phenotypes**
Will be computed using the [Monarch Phenotype Profile Analysis tool](https://monarchinitiative.org/analyze/phenotypes). The 5 highest scored computed phenotypes obtained by submitting a patient's HPO terms to Monarch will be used for patient matching. The similarity between computed phenotypes **will make up 1/4 of the of the maximum similarity score between two patient. For patients with no OMIM diagnosis (empty disorders field) the Monarch phenotypes will count for half of the maximum similarity score between two patient**

- **Disorders**
OMIM diagnoses, if available, will make up **1/4 of the maximum similarity score**.



[travis-url]: https://travis-ci.org/Clinical-Genomics/patientMatcher
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/patientMatcher.svg?style=flat-square
