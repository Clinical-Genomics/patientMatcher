FROM mongo:4.0.7-xenial

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    bzip2 \
    ca-certificates \
    curl \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    wget \
    vim && \
    apt-get clean

WORKDIR /root

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.11-Linux-x86_64.sh -O ~/miniconda.sh && \
        /bin/bash ~/miniconda.sh -b -p /opt/conda && \
        rm ~/miniconda.sh && \
        /opt/conda/bin/conda clean -tipsy && \
        ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
        echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
        echo "conda activate base" >> ~/.bashrc && \
        echo "echo 'in roots bashrc'" >> ~/.bashrc

RUN mongod --fork --syslog && \
    echo 'conn = new Mongo();db = conn.getDB("pmatcher");db.disableFreeMonitoring(); db.createUser({user: "pmUser", pwd: "pmPassword", roles:["dbOwner"]});' > setup_mongo.js && \
    mongo setup_mongo.js

COPY . /opt/patientMatcher

WORKDIR /opt/patientMatcher

RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    pip install -U pip setuptools && \
    pip install -e .

EXPOSE 5000

CMD ["/bin/bash", "--rcfile", "/root/.bashrc", "-c", "pmatcher", "run"]
