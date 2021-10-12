import os

# Turns on debugging features in Flask
DEBUG = True

# secret key:
SECRET_KEY = "MySuperSecretKey"

DB_USERNAME = "pmUser"
DB_PASSWORD = "pmPassword"
DB_NAME = "pmatcher"
DB_HOST = (
    os.getenv("MONGODB_HOST") or "127.0.0.1"
)  # simply substitute with 'mongodb' if connecting to MongoDB running in a container
DB_PORT = os.getenv("MONGODB_PORT") or 27017

# DB_URI = "mongodb://{}:{}@{}:{}/{}".format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
DB_URI = "mongodb://{}:{}/{}".format(DB_HOST, DB_PORT, DB_NAME)  # without authentication
# DB_URI = "mongodb://127.0.0.1:27011,127.0.0.1:27012,127.0.0.1:27013/?replicaSet=rs0&readPreference=primary"  # MongoDB replica set


# Matching Algorithms scores
# sum of MAX_GT_SCORE and MAX_PHENO_SCORE should be 1
MAX_GT_SCORE = 0.75
MAX_PHENO_SCORE = 0.25

# Max results matches returned by server.
MAX_RESULTS = 5

# Set a minimum patient score threshold for returned results
# Set this parameter to 0 to return all results with a score higher than 0
SCORE_THRESHOLD = 0

# Disclaimer. This text is returned along with match results or server metrics
DISCLAIMER = """PatientMatcher provides data in good faith as a research tool and makes no warranty nor assumes any legal responsibility for any purpose for which the data is used. Users should not attempt in any case to identify patients whose data is returned by the service. Users who intend to publish papers using this software should acknowledge PatientMatcher and its developers (https://www.scilifelab.se/facilities/clinical-genomics-stockholm/)."""

# Email notification params.
# Required only if you want to send match notifications to patients contacts
# MAIL_SERVER = mail_port
# MAIL_PORT = email_port
# MAIL_USE_TLS = True or False
# MAIL_USE_SSL = True or False
# MAIL_USERNAME = 'user_email@mail.se'
# MAIL_PASSWORD = 'mail_password'

# ADMINS will receive email notification is app crashes
# ADMINS = []

# Set NOTIFY_COMPLETE to False if you don't want to notify variants and phenotypes by email
# This way only contact info and matching patients ID will be notified in email body
# NOTIFY_COMPLETE = True
