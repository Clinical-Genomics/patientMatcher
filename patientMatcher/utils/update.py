# -*- coding: utf-8 -*-
import logging

import requests
from clint.textui import progress
from patientMatcher.constants import PHENOTYPE_TERMS

LOG = logging.getLogger(__name__)


def update_resources(test=True):
    """Download phenotype files necessary to perform phenotype matching"""

    for key, item in PHENOTYPE_TERMS.items():
        destination = item["resource_path"]
        url = item["url"]

        r = requests.get(url, stream=True)
        total_length = int(r.headers.get("content-length"))

        if total_length == 0:  # read file and get its size
            LOG.warning(f"Could not verify file {key} at the requested url:{url}")

        if test or total_length == 0:
            LOG.warning(f"File {key} has a length of {total_length}")
            continue

        with open(destination, "wb") as f:  # overwrite file
            for chunk in progress.bar(
                r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1
            ):
                if chunk:
                    f.write(chunk)
                    f.flush()
        LOG.debug(f"File {key} written to disk")
