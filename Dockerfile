FROM clinicalgenomics/python3.8-slim-bullseye-venv:1.0

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

# Install and run commands from virtual environment
RUN python3 -m venv /home/worker/venv
ENV PATH="/venv/bin:$PATH"

# Create a non-root user to run commands
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --create-home worker

WORKDIR /home/worker/app
COPY . /home/worker/app

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir -e .

# Run commands as non-root user
USER worker

ENTRYPOINT ["pmatcher"]
