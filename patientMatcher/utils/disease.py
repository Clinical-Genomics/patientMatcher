# -*- coding: utf-8 -*-
# These classes are a simplified version of Disease and Diseases classes
# originally developed by Orion Buske in patient-similarity (https://github.com/buske/patient-similarity)

import logging
import re
from collections import defaultdict

from patientMatcher.resources import path_to_phenotype_annotations

LOG = logging.getLogger(__name__)
db_re = re.compile("([A-Z]+:\d+)")

FREQUENCY_TERMS = {
    "HP:0040280": 1.0,  # Obligate
    "HP:0040281": (0.99 + 0.80) / 2.0,  # Very frequent
    "HP:0040282": (0.79 + 0.30) / 2.0,  # Frequent
    "HP:0040283": (0.05 + 0.29) / 2.0,  # Occasional
    "HP:0040284": (0.01 + 0.04) / 2.0,  # Very rare
    "HP:0040285": 0.0,  # Excluded
}

FREQUENCIES = {
    "very rare": 0.01,
    "rare": 0.05,
    "occasional": 0.075,
    "frequent": 0.33,
    "typical": 0.5,
    "variable": 0.5,
    "common": 0.75,
    "hallmark": 0.9,
    "obligate": 1.0,
}


class Disease:
    """An object representing a single disease"""

    def __init__(self, db, db_id, phenotypes):
        self.db = db
        self.id = db_id
        self.phenotype_freqs = phenotypes

    def __str__(self):
        return f"{self.db}:{self.id}"


class Diseases:
    """Create an object containing all diseases from the phenotype_annotations.tav.txt file
    Resources included in this file: DECIPHER, OMIM, ORPHANET
    """

    def init_app(self, app):
        """Initialize the diseases object when the app is launched"""
        self.databases = ["DECIPHER", "OMIM", "ORPHA"]
        self.diseases = {}
        self._parse_diseases()
        LOG.info(f"Parsed {len(self.diseases.keys())} disease/phenotypes from resource file")

    def _parse_disease_frequency(self, field):
        """Parse disease frequency (col 8 in phenotype anno file)"""
        if not field:
            return None

        if field.upper() in FREQUENCY_TERMS:
            return FREQUENCY_TERMS[field]

        field = field.lower()

        if field in FREQUENCIES:
            return FREQUENCIES[field]
        if field.endswith("%"):
            field = field.replace("%", "")
            if "-" in field:
                # Average any frequency ranges
                low, high = field.split("-")
                freq = (float(low) + float(high)) / 2 / 100
            else:
                freq = float(field) / 100
        else:
            try:
                num, denom = fraction_frequency_re.split(field)
            except Exception as ex:
                LOG.warning(f"Error parsing frequency: {field} -> {ex}")
                freq = default
            else:
                freq = float(num) / float(denom)
        return freq

    def _parse_diseases(self):
        """Parse diseases file, that is available under patientMatcher/resources"""
        disease_phenotypes = defaultdict(dict)
        with open(path_to_phenotype_annotations, encoding="utf-8") as disease_file:
            for line in disease_file:
                diseases = []
                line = line.strip()
                items = line.split("\t")

                db = items[0]
                if db not in self.databases:
                    continue
                diseases.append((items[0].strip(), items[1].strip()))  # diseases: [(OMIM, 102400)]

                # Add alternative terms to list of diseases
                alt_diseases = db_re.findall(items[5].strip())  # example: ['OMIM:147791']
                for alt_disease in alt_diseases:
                    alt_db = alt_disease.split(":")[0].strip()
                    alt_db_id = int(alt_disease.split(":")[1].strip())
                    if alt_db in ["MIM", "IM"]:
                        alt_db = "OMIM"
                    if alt_db not in self.databases:
                        continue
                    diseases.append((alt_db, alt_db_id))

                # Add HPO terms and frequencies to disease terms
                hpo_term = items[4].strip()
                freq = self._parse_disease_frequency(items[8])
                for disease in diseases:
                    phenotypes = disease_phenotypes[disease]
                    # Collect max annotated frequency
                    if freq is not None and hpo_term in phenotypes:
                        old_freq = phenotypes[hpo_term]
                        if old_freq is None or old_freq < freq:
                            phenotypes[hpo_term] = freq
                        if old_freq != freq:
                            pass
                    else:
                        phenotypes[hpo_term] = freq
                    # phenotypes[hpo_term] = None  # Do not populate disease frequencies

        for (db, db_id), phenotypes in disease_phenotypes.items():
            disease = Disease(db, db_id, phenotypes)
            self.diseases[(db, db_id)] = disease
