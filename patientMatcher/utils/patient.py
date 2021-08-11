# -*- coding: utf-8 -*-

import logging

LOG = logging.getLogger(__name__)


class Patient(object):
    def __init__(self, pat_id, hp_terms):
        self.id = pat_id
        self.hp_terms = hp_terms
        self._ancestors = None

    def ancestors(self):
        """Return all the HPO terms ancestors for a patient"""
        if self._ancestors is None:
            ancestors = set()
            for term in self.hp_terms:
                ancestors.update(term.ancestors())
            self._ancestors = ancestors
        return self._ancestors


def pheno_similarity_score_simgic(hpoic, patient1, patient2):
    """Compare 2 patients phenotypes using the simgic algorithm"""
    LOG.info(f"Comparing patient1.id vs patient2.id")

    p1_ancestors = patient1.ancestors()
    p2_ancestors = patient2.ancestors()

    common_ancestors = p1_ancestors & p2_ancestors  # min
    all_ancestors = p1_ancestors | p2_ancestors  # max

    return hpoic.information_content(common_ancestors) / hpoic.information_content(all_ancestors)


def patients(database, ids=None):
    """Get all patients in the database

    Args:
        database(pymongo.database.Database)
        ids(list): a list of IDs to return only specified patients

    Returns:
        results(Iterable[dict]): list of patients from mongodb patients collection
    """
    results = None
    query = {}
    if ids:  # if only specified patients should be returned
        LOG.info("Querying patients for IDs {}".format(ids))
        query["_id"] = {"$in": ids}

    else:
        LOG.info("Return all patients in database")

    results = database["patients"].find(query)
    return results
