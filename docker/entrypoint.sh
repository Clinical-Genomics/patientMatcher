#!/bin/bash

if [[ -z $(which python) ]]; then
    . /opt/conda/etc/profile.d/conda.sh
    conda activate patientMatcher
    python -V
fi

SETUP_JS=/root/setup_mongo.js
cat > $SETUP_JS << EOF
conn = new Mongo();
db = conn.getDB("pmatcher");
db.disableFreeMonitoring();
db.createUser({user: "pmUser", pwd: "pmPassword", roles:["dbOwner"]});
EOF

mongod --fork \
    --pidfilepath $MONGO_PIDFILE \
    --logpath $MONGO_LOGPATH --logappend
mongo $SETUP_JS

pmatcher add demodata
pmatcher add client -id test_client -token test_token -url www.test-url.com

exec "$@"
