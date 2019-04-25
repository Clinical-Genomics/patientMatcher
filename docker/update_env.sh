#!/bin/bash -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# We're running this inside the previously built container to ensure
# the OS/container environment matches what it will be run in.

if [[ -z $INSIDE_THE_CONTAINER ]]; then
    docker run -e INSIDE_THE_CONTAINER=1 \
        -v $DIR/..:/opt/patientMatcher \
        --rm \
        -it \
        --entrypoint /opt/patientMatcher/docker/update_env.sh \
        local/patientmatcher
else
    export DOCKER_CONDA_PREFIX=/opt/conda/envs/patientMatcher
    export DOCKER_ENV_NAME=patientMatcher
    TEMP_ENV_NAME="temp-${DOCKER_ENV_NAME}"
    PYTHON_VERSION=3.6.8

    # conda functions don't get exported to subshells, so source it
    source /opt/conda/etc/profile.d/conda.sh

    conda create -y --name $TEMP_ENV_NAME python=${PYTHON_VERSION}
    conda activate $TEMP_ENV_NAME
    conda install git -y
    pip install -r $DIR/../requirements.txt -r $DIR/../requirements-dev.txt
    conda env export --no-builds \
        | perl -wlne 'if ($. == 1){print "name: $ENV{DOCKER_ENV_NAME}"} elsif (/^prefix:/){print "prefix: $ENV{DOCKER_CONDA_PREFIX}"} else {print}' \
        > $DIR/conda_env.yml
    conda deactivate
    conda env remove --name $TEMP_ENV_NAME
fi
