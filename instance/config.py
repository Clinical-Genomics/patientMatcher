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
