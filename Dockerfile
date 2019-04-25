FROM mongo:4.0.7-xenial

SHELL ["/bin/bash", "-c"]

ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHON_VERSION 3.6
ENV MONGO_PIDFILE /opt/patientMatcher/mongod.pid
ENV MONGO_LOGPATH /opt/patientMatcher/mongod.log

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

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
        /bin/bash ~/miniconda.sh -b -p /opt/conda && \
        rm ~/miniconda.sh && \
        ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
        echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
        echo "conda activate patientMatcher" >> ~/.bashrc

COPY . /opt/patientMatcher

WORKDIR /opt/patientMatcher

RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda install -y conda=4.6.* && \
    conda env create -f /opt/patientMatcher/docker/conda_env.yml && \
    conda clean -tipsy && \
    conda activate patientMatcher && \
    pip install git+https://github.com/Clinical-Genomics/patient-similarity && \
    pip install -e .

ENTRYPOINT [ "docker/entrypoint.sh" ]
CMD [ "pmatcher", "run", "-h", "0.0.0.0" ]
