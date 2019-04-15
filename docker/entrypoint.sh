#!/bin/bash -e

CURR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ -z $(which python) ]]; then
    . /opt/conda/etc/profile.d/conda.sh
    conda activate patientMatcher
fi

# ugly grep, but lets user mount custom `instance/config.py` into image
DB_USERNAME=$(grep '^DB_USERNAME =' $CURR_DIR/../patientMatcher/instance/config.py | cut -f 3 -d' ' | tr -d \')
DB_PASSWORD=$(grep '^DB_PASSWORD =' $CURR_DIR/../patientMatcher/instance/config.py | cut -f 3 -d' ' | tr -d \')
DB_NAME=$(grep '^DB_NAME =' $CURR_DIR/../patientMatcher/instance/config.py | cut -f 3 -d' ' | tr -d \')

SETUP_JS=/root/setup_mongo.js
cat > $SETUP_JS << EOF
conn = new Mongo();
db = conn.getDB("$DB_NAME");
db.disableFreeMonitoring();
db.createUser({user: "$DB_USERNAME", pwd: "$DB_PASSWORD", roles:["dbOwner"]});
EOF

mongod --fork \
    --pidfilepath $MONGO_PIDFILE \
    --logpath $MONGO_LOGPATH --logappend
mongo $SETUP_JS

pmatcher add demodata
pmatcher add client -id test_client -token test_token -url www.test-url.com

exec "$@"
