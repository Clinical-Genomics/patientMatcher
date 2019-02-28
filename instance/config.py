#Turns on debugging features in Flask
DEBUG = True

#secret key:
SECRET_KEY = 'MySuperSecretKey'

# Database connection string
DB_URI = "mongodb://pmUser:pmPassword@127.0.0.1:27017/pmatcher"
DB_NAME = "pmatcher"

# Matching Algorithms scores
# sum of MAX_GT_SCORE and MAX_PHENO_SCORE should be 1
MAX_GT_SCORE = 0.5
MAX_PHENO_SCORE = 0.5

# Max results matches returned by server.
MAX_RESULTS = 5

# Disclaimer. This text is returned along with match results or server metrics
DISCLAIMER = 'patientMatcher provides data in good faith as a research tool. patientMatcher makes no warranty nor assumes any legal responsibility for any purpose for which the data are used. Users should not attempt in any case to identify patients whose data is returned by the service. Users who intend to publish paper using this software should acknowldge patientMatcher and its developers (https://www.scilifelab.se/facilities/clinical-genomics-stockholm/).'

# Server Host. Used when submitting queries and returning results
MME_HOST = 'https://www.scilifelab.se/facilities/clinical-genomics-stockholm'

# Email notification params.
# Required only if you want to send match notifications to patients contacts
#MAIL_SERVER = smtp_server
#MAIL_PORT = mail_port
#MAIL_USE_SSL = True or False
#MAIL_USERNAME = mail_username
#MAIL_PASSWORD = mail_password
