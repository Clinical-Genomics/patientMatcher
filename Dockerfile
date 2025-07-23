FROM ghcr.io/astral-sh/uv:python3.12-bookworm

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

# Create virtual environment
RUN python3 -m venv /home/worker/venv
ENV PATH="/home/worker/venv/bin:$PATH"

# Create a non-root user
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --create-home worker

# Set working directory and copy project metadata for caching
WORKDIR /home/worker/app
COPY pyproject.toml uv.lock ./

# Install dependencies with uv from the preinstalled binary
RUN python3 -m venv /home/worker/venv \
 && . /home/worker/venv/bin/activate \
 && uv sync --frozen --no-install-project --no-editable

# Copy rest of source code
COPY . .

# Ensure logs reach console immediately
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER worker

# Start the app
ENTRYPOINT ["pmatcher"]
