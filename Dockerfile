FROM python:3.8-alpine3.12

LABEL base_image="python:3.8-alpine3.12"
LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

RUN apk update
# Install required libs
RUN apk --no-cache add git bash

# Install patient_similarity from a fork @ClinicalGenomics
# Original repo: https://github.com/buske/patient-similarity
RUN pip install git+https://github.com/Clinical-Genomics/patient-similarity

WORKDIR /home/worker/app
COPY . /home/worker/app

# Install requirements
RUN pip install -r requirements.txt

# Install the app
RUN pip install -e .

# Run commands as non-root user
RUN adduser -D worker
RUN chown worker:worker -R /home/worker
USER worker
