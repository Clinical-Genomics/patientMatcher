## Server endpoints

### **/patient/add**
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



### **/patient/delete/<patient_id>**
&nbsp;You can delete a patient from the database by sending a **DELETE** request with its ID to the server. Example:
```bash
curl -X DELETE \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/patient/delete/patient_id
```
Please note that when a patient is deleted all its match results will be also deleted from the database. This is valid for **matches where the patient was used as the query patient** in searches performed on other nodes or the internal patientMatcher database (internal search).
Matching results where the removed patient is instead listed among the matching results will be not removed from the database.

&nbsp;&nbsp;


### **/metrics**
&nbsp;Use this endpoint to **get** database metrics.<br>
Stats which could be retrieved by a MME service are described [here](https://github.com/ga4gh/mme-apis/blob/master/metrics-api.md)<br>
Example:
```bash
curl -X GET \
  localhost:9020/metrics
```
&nbsp;&nbsp;


### **/nodes**
&nbsp;**GET** the list of connected nodes. Example:
```bash
curl -X GET \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/nodes
```
The response will return a list like this : [ { 'id' : node_1_id, 'description' : node1_description }, .. ] or an empty list if the server is not connected to external nodes.

&nbsp;&nbsp;


### **/match**
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


### **/match/external/<patient_id>**
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


### **/matches/<patient_id>**
&nbsp;Return all matches (internal and external) with positive results for a patient specified by an ID. Example:
```bash
curl -X GET \
  -H 'X-Auth-Token: DEMO' \
  localhost:9020/matches/patient_id
```
