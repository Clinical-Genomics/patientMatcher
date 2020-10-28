FROM python:3.8-alpine3.12

LABEL version="1"
LABEL about.license="MIT License (MIT)"
LABEL software.version="2.3"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"
LABEL maintainer="Chiara Rasi <chiara.rasi@scilifelab.se>"

RUN apk update
# Install required libs
RUN apk --no-cache add git

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
