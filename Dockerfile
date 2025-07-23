FROM clinicalgenomics/python3.12-venv:1.0

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

# Install and run commands from virtual environment
RUN python3 -m venv /home/worker/venv
ENV PATH="/home/worker/venv/bin:$PATH"

# Install uv into the virtual environment
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --yes --root /home/worker/venv

# Create a non-root user to run commands
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --create-home worker

WORKDIR /home/worker/app
COPY . /home/worker/app

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

# Install the project in editable mode (NOTE: uv does not support editable installs as of now)
# So we fallback to standard install
RUN uv pip install --no-deps --no-cache-dir .

# Run commands as non-root user
USER worker

ENTRYPOINT ["pmatcher"]
