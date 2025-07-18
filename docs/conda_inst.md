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
poetry install
```

To customize the server configuration you'll need to edit the **config.py** file under the /instance folder. &nbsp;
For testing purposes you can keep the default configuration values as they are, but keep in mind that you should adjust these numbers when in production.

To start the server run this command:
```bash
poetry run pmatcher run -h custom_host -p custom_port
```
Please note that the code is NOT guaranteed to be bug-free and it must be customized to be used in production.
