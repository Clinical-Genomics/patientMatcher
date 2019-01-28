#Turns on debugging features in Flask
DEBUG = True

#secret key:
SECRET_KEY = 'MySuperSecretKey'

#server host and port
#HOST = "127.0.0.1"
#PORT = 9020

# Database connection string
DB_URI = "mongodb://pmUser:pmPassword@127.0.0.1:27017/pmatcher"
DB_NAME = "pmatcher"

# Matching Algorithms scores
# sum of MAX_GT_SCORE and MAX_PHENO_SCORE should be 1
MAX_GT_SCORE = 0.5
MAX_PHENO_SCORE = 0.5

# Max results matches returned by server.
MAX_RESULTS = 5

# Email notification params.
# Required only if you want to send match notifications to patients contacts
#MAIL_SERVER = smtp_server
#MAIL_PORT = mail_port
#MAIL_USE_SSL = True or False
#MAIL_USERNAME = mail_username
#MAIL_PASSWORD = mail_password
