###########
# BUILDER #
###########
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS python-builder

WORKDIR /app

# Copy the project files needed to configure dependencies build into the image
COPY --chmod=644 pyproject.toml uv.lock README.md ./

RUN uv venv --relocatable
RUN uv sync --frozen --no-install-project --no-editable

#########
# FINAL #
#########
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

LABEL about.license="MIT License (MIT)"
LABEL about.tags="WGS,WES,Rare diseases,VCF,variants,phenotype,OMIM,HPO,variants"
LABEL about.home="https://github.com/Clinical-Genomics/patientMatcher"

# Create a non-root user
RUN groupadd --gid 1000 worker && useradd -g worker --uid 1000 --shell /usr/sbin/nologin --create-home worker

ENV PATH="/home/worker/app/.venv/bin:$PATH"

# Set working directory and copy project metadata for caching
WORKDIR /home/worker/app

# Copy current app code to app dir
COPY --chown=root:root --chmod=755 . /home/worker/app

# Copy virtual environment from builder
COPY --chown=root:root --chmod=755 --from=python-builder /app/.venv /home/worker/app/.venv

# Install the app
RUN uv pip install --no-cache-dir --editable .

# Ensure logs reach console immediately
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER worker

# Start the app
ENTRYPOINT ["uv", "run", "pmatcher"]
