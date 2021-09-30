print('########### Setting up PatientMatcher database user ###########');

db = db.getSiblingDB('pmatcher');
db.createUser(
   {
     user: "pmUser",
     pwd: "pmPassword",
     roles: [ "dbOwner" ]
   }
)
