FROM python:3.8-alpine3.12

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

RUN apk update
# Install required libs
RUN apk --no-cache add git bash

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install the app
RUN pip install --no-cache-dir -e .

# Run commands as non-root user
RUN adduser -D worker &&\
chown worker:worker -R /home/worker
USER worker
