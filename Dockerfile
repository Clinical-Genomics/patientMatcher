FROM clinicalgenomics/python3.8-venv:1.0

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

# Install and run commands from virtual environment
RUN echo export PATH="/venv/bin:\$PATH" > /etc/profile.d/venv.sh

RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --create-home worker

WORKDIR /home/worker/app
COPY . /home/worker/app

RUN pip install --no-cache-dir -e .

# Run commands as non-root user
USER worker

ENTRYPOINT ["pmatcher"]
