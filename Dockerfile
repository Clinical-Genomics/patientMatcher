FROM mongo:4.0.7-xenial

SHELL ["/bin/bash", "-c"]

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV MONGO_PIDFILE /var/run/mongod.pid
ENV MONGO_LOGPATH /var/log/mongodb/mongod.log

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

ENV CONDA_VERSION 4.6.14
COPY docker/conda_env.yml /root/conda_env.yml
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
        /bin/bash ~/miniconda.sh -b -p /opt/conda && \
        rm ~/miniconda.sh && \
        ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
        echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
        echo "conda activate patientMatcher" >> ~/.bashrc && \
        source /opt/conda/etc/profile.d/conda.sh && \
        conda install -y conda=$CONDA_VERSION && \
        conda env create -f /root/conda_env.yml && \
        conda clean -tipsy

COPY . /opt/patientMatcher
WORKDIR /opt/patientMatcher
RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda activate patientMatcher && \
    pip install git+https://github.com/Clinical-Genomics/patient-similarity && \
    pip install -e .

ENTRYPOINT [ "docker/entrypoint.sh" ]
CMD [ "pmatcher", "run", "-h", "0.0.0.0", "-p", "9020" ]
