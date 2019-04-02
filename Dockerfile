FROM mongo:4.0.7-xenial

SHELL ["/bin/bash", "-c"]

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
        /opt/conda/bin/conda clean -tipsy && \
        ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
        echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
        source /opt/conda/etc/profile.d/conda.sh && \
        conda create --name patientMatcher python=${PYTHON_VERSION} && \
        echo "conda activate patientMatcher" >> ~/.bashrc

COPY . /opt/patientMatcher

WORKDIR /opt/patientMatcher

RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda activate patientMatcher && \
    pip install -U pip setuptools && \
    pip install -r requirements.txt -r requirements-dev.txt && \
    pip install pytest-cov coveralls && \
    pip install -e .

ENTRYPOINT [ "docker/entrypoint.sh" ]
CMD [ "pmatcher", "run" ]
