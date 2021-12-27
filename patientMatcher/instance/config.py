import os

# Turns on debugging features in Flask
DEBUG = os.getenv("DEBUG") or True

# Set to False is app if a production app
TESTING = os.getenv("TESTING") or True

# secret key:
SECRET_KEY = os.getenv("SECRET_KEY") or "MySuperSecretKey"

DB_USERNAME = os.getenv("MONGODB_USER") or "pmUser"
DB_PASSWORD = os.getenv("MONGODB_PASSWORD") or "pmPassword"
DB_NAME = os.getenv("MONGODB_DBNAME") or "pmatcher"
DB_HOST = (
    os.getenv("MONGODB_HOST") or "127.0.0.1"
)  # simply substitute with 'mongodb' if connecting to MongoDB running in a container
DB_PORT = os.getenv("MONGODB_PORT") or 27017

# DB_URI = "mongodb://{}:{}@{}:{}/{}".format(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
DB_URI = os.getenv("MONGODB_DB_URI") or "mongodb://{}:{}/{}".format(
    DB_HOST, DB_PORT, DB_NAME
)  # without authentication
# DB_URI = "mongodb://127.0.0.1:27011,127.0.0.1:27012,127.0.0.1:27013/?replicaSet=rs0&readPreference=primary"  # MongoDB replica set

# Matching Algorithms scores
# sum of MAX_GT_SCORE and MAX_PHENO_SCORE should be 1
MAX_GT_SCORE = os.getenv("MAX_GT_SCORE") or 0.75
MAX_PHENO_SCORE = os.getenv("MAX_PHENO_SCORE") or 0.25

# Max results matches returned by server.
MAX_RESULTS = os.getenv("MAX_RESULTS") or 5

# Set a minimum patient score threshold for returned results
# Set this parameter to 0 to return all results with a score higher than 0
SCORE_THRESHOLD = os.getenv("SCORE_THRESHOLD") or 0

# Disclaimer. This text is returned along with match results or server metrics
DISCLAIMER = (
    os.getenv("DISCLAIMER")
    or """PatientMatcher provides data in good faith as a research tool and makes no warranty nor assumes any legal responsibility for any purpose for which the data is used. Users should not attempt in any case to identify patients whose data is returned by the service. Users who intend to publish papers using this software should acknowledge PatientMatcher and its developers (https://www.scilifelab.se/facilities/clinical-genomics-stockholm/)."""
)

# Email notification params.
# Required only if you want to send match notifications to patients contacts
MAIL_SERVER = os.getenv("MAIL_SERVER") or None  # "smtp.gmail.com"
MAIL_PORT = os.getenv("MAIL_PORT") or None  # 587
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") or True  # True
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") or False  # False
MAIL_USERNAME = os.getenv("MAIL_USERNAME") or None  # some.email@test.se
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD") or None  # email_password

# ADMINS will receive email notification is app crashes
ADMINS = os.getenv("ADMINS") or ["test.email@mail.se"]

# Set NOTIFY_COMPLETE to False if you don't want to notify variants and phenotypes by email
# This way only contact info and matching patients ID will be notified in email body
NOTIFY_COMPLETE = os.getenv("NOTIFY_COMPLETE") or False
