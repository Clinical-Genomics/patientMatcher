FROM tiangolo/uvicorn-gunicorn:python3.8-slim

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

RUN apt-get update && \
    apt-get -y upgrade && \
    apt-get -y install -y --no-install-recommends bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 1000 worker && useradd -g worker --uid 10001 --create-home worker

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install the app
RUN pip install --no-cache-dir -e .

# Run commands as non-root user
USER worker

ENTRYPOINT ["/bin/bash"]
