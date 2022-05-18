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
pmatcher add demodata
```
Please note that the list of benchmarking patients all gene ids are represented as HGNC gene symbols.
The command above will convert gene symbols to Ensembl ids, in accordance to the GA4GH API: https://github.com/ga4gh/mme-apis/blob/master/search-api.md.

The above command will also load a demo client with token `DEMO` into the database
&nbsp;&nbsp;

<a name="cli_remove_patient"></a>
### Removing a patient from the database.
You can remove a patient using the command line interface by invoking this command and providing **either its ID or its label** (or both actually):

```bash
pmatcher remove patient [OPTIONS]

Options:
--id TEXT     ID of the patient to be removed from database
--label TEXT  label of the patient to be removed from database
```
&nbsp;&nbsp;

<a name="cli_update_contacts"></a>
### Updating patients' contact info using the command line
Contact information is a mandatory descriptor for each patient and represents the primary contact email address or URL used when looking for additional information for a patient in case of positive matches triggered by other patients from external nodes or the same database. A patient contact is described in PatientMatcher (and in the MatchMaker Exchange API) by these key/values:

- **href**: a string represented by a URL (example: http://www.ncbi.nlm.nih.gov/pubmed/23542699) or the email address of the contact user (example: mailto:someone@somesite.com). This field is mandatory.
- **name**: complete name of the contact user responsible for the patient saved in the MatchMaker. This field is mandatory.
- **institution**: the Institution the contact person for the patients belongs to. This information is optional.

The command to update patients' contact info is the following:
```bash
pmatcher update contact [OPTIONS]

  Update contact person for a group of patients

Options:
  --old-href TEXT     Old contact href  [required]
  --href TEXT         New contact href  [required]
  --name TEXT         New contact name  [required]
  --institution TEXT  New contact institution
```

Let's assume a group of patients has a contact `Peter Parker` with href `mailto:pparker@example.com`. To replace the old user contact in **all patients** with the new contact info, for instance `Bruce Wayne`, type:

```bash
pmatcher update contact --old-href maito:pparker@example.com --href mailto:bwayne@example.com -name "Bruce Wayne" -institution "Wayne Enterprises, Inc."
```

<a name="cli_add_client"></a>
### Adding a client to the database
In order to save patients into patientMatcher you need to create at least one authorized client.&nbsp;
Use the following command to insert a client object in the database:

```bash
pmatcher add client [OPTIONS]

Options:
--id TEXT       Client ID  [required]
--token TEXT    Authorization token  [required]
--url TEXT      Client URL  [required]
--contact TEXT  Client email
```
POST request aimed at adding or modifying a patient in patientMatcher **should be using a token** from a client present in the database.&nbsp;
Clients may be from the command line with this command:
```bash
pmatcher remove client --id client_id
```
&nbsp;&nbsp;

<a name="cli_add_node"></a>
### Adding a connected node to the database
To connect to another MME node and submit requests to it you should know the authentication token to the other node.&nbsp;
You can add a node to the database by running the command:

```bash
pmatcher add node [OPTIONS]

Options:
  --id TEXT                Server/Client ID  [required]
  --token TEXT             Authorization token  [required]
  --matching_url TEXT      URL to send match requests to  [required]
  --accepted_content TEXT  Accepted Content-Type  [required]
  --contact TEXT           An email address
```
Connected nodes may be removed any time using the command:&nbsp;
```bash
pmatcher remove node --id node_id
```
&nbsp;&nbsp;
