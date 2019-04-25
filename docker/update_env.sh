#!/bin/bash -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

export DOCKER_CONDA_PREFIX=/opt/conda/envs/patientMatcher
export DOCKER_ENV_NAME=patientMatcher
TEMP_ENV_NAME="temp-${DOCKER_ENV_NAME}"
PYTHON_VERSION=3.6.8

if [[ -z $(which conda) ]]; then
    echo "You must have conda installed to update conda_env.yml"
    exit 1
fi
source $(conda info --base)/etc/profile.d/conda.sh

conda create -y --no-default-packages --name $TEMP_ENV_NAME python=${PYTHON_VERSION}
conda activate $TEMP_ENV_NAME
conda install git -y --channel defaults --override-channels
pip install -r $DIR/../requirements.txt -r $DIR/../requirements-dev.txt
conda env export \
    | perl -wlne '$IN_CHAN = (/^channels:/ || ($IN_CHAN && /^ /)) ? 1 : 0; if ($. == 1){print "name: $ENV{DOCKER_ENV_NAME}"} elsif ($IN_CHAN) {next} elsif (/^prefix:/){print "prefix: $ENV{DOCKER_CONDA_PREFIX}"} else {print}' \
    > $DIR/conda_env.yml
conda deactivate
conda env remove --name $TEMP_ENV_NAME
