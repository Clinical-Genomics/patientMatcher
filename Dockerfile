FROM clinicalgenomics/python3.12-venv:1.0

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

# Set up virtual environment
RUN python3 -m venv /home/worker/venv
ENV PATH="/home/worker/venv/bin:$PATH"

# Install uv into the virtual environment
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --yes --root /home/worker/venv

# Create a non-root user
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --create-home worker

# Set working directory and copy only project metadata first for caching
WORKDIR /home/worker/app
COPY pyproject.toml uv.lock ./

# Install dependencies from lockfile (no editable mode)
RUN uv pip install --system --no-deps

# Copy the rest of the source code
COPY . .

# Ensure logs are unbuffered
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER worker

# Start the application
ENTRYPOINT
