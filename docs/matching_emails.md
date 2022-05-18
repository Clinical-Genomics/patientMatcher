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
