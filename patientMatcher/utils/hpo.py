# -*- coding: utf-8 -*-
# These classes are a simplified version of HPO and HPOIC classes
# originally developed by Orion Buske in patient-similarity (https://github.com/buske/patient-similarity)

import logging
from collections import defaultdict
from math import log

from patientMatcher.resources import path_to_hpo_terms

LOG = logging.getLogger(__name__)

ROOT = "HP:0000001"

### Code required by the HPO class ###
def get_ancestors(root, acc=None):
    if acc is None:
        acc = set()
    acc.add(root)
    for parent in root.parents:
        get_ancestors(parent, acc)
    return acc


class HPNode(object):
    """Populate an HPO object node from a list of lines in the HPO ontology file"""

    def __init__(self, hpo_lines):
        self.id = None
        self.name = None
        self.parents = set()
        self.children = set()
        self.alts = set()  # Alternative Ids
        self._parent_hps = set()
        self.obsolete = False

        if hpo_lines[0] != "[Term]":
            return

        for line in hpo_lines[1:]:
            field, value = line.split(": ", 1)
            if field == "id" and value.startswith("HP:"):
                self.id = value
            elif field == "name":
                self.name = value
            elif field == "is_a":
                hp = value.split(" !")[0]
                self._parent_hps.add(hp)
            elif field == "alt_id":
                self.alts.add(value)
            if field == "is_obsolete":
                self.obsolete = True

    def ancestors(self):
        """return all node ancestors"""
        return get_ancestors(self)

    def validate(self):
        """Make sure a node has an ID, a name and parents (if node is not root)"""
        return bool(self.id) and bool(self.name) and self.obsolete is False

    def link(self, hps):
        """Link a node objects to its parents and children on the ontology tree"""
        for hp in self._parent_hps:
            parent = hps.get(hp)
            self.parents.add(parent)
            parent.children.add(self)

    def __str__(self):
        return str(self.id)


class HPO(object):
    """Parse and HPO ontology to make it available for phenotype matching"""

    def init_app(self, app):
        """Initialize the HPO ontology when the app is launched."""
        self.hps = {}
        self._parse_ontolology()
        self.root = self.hps[ROOT]

    def _parse_ontolology(self):
        """Parse HPO ontology file, that is available under patientMatcher/resources"""
        with open(path_to_hpo_terms, encoding="utf-8") as hpofile:
            hpo_lines = []  # A group of lines containing data for an HPO term
            for line in hpofile:
                line = line.strip()
                if not line:
                    # If there is an empty line reset HPO lines
                    # since a the lines for a new HPO terms are about to start
                    hp_node = HPNode(hpo_lines)
                    # Don't take into account file header lines or obsolete terms
                    if hp_node.validate() is True:
                        self.hps[hp_node.id] = hp_node

                    # Include also alternate node IDs in hps dictionary
                    for hpid in hp_node.alts:
                        if hpid in self.hps:
                            continue
                        self.hps[hpid] = hp_node

                    hpo_lines = []  # Reset lines for next HPO term
                    continue
                hpo_lines.append(line)

        # Connect HP objects in a tree
        nodes = set(self.hps.values())

        for node in nodes:
            node.link(self.hps)

        LOG.info(f"Parsed {len(nodes)} HPO terms into HPO nodes from resource file")

    def __getitem__(self, key):
        return self.hps[key]

    def __len__(self):
        return len(set(self.hps.values()))


### End of  code required by the HPO class ###


### Code required by the HPOIC class ###
EPS = 1e-9


def _bound(p, eps=EPS):
    return min(max(p, eps), 1 - eps)


###  Class handling the information-content functionality for the HPO
class HPOIC(object):
    def init_app(self, app, hpo, diseases):
        """Initialize the HPO ontology when the app is launched."""
        LOG.info("Initializing the HPO information content")
        term_freq = self._get_term_frequencies(diseases, hpo)
        LOG.info("Total term frequency mass: {}".format(sum(term_freq.values())))
        term_ic = self._get_ics(hpo.root, term_freq)
        LOG.info("IC calculated for {}/{} terms".format(len(term_ic), len(hpo)))
        lss = self._get_link_strengths(hpo.root, term_ic)
        LOG.info("Link strength calculated for {}/{} terms".format(len(lss), len(hpo)))
        self.term_ic = term_ic
        self.lss = lss

        for term, ic in term_ic.items():
            for p in term.parents:
                assert ic >= term_ic[p] - EPS, str((term, ic, term_ic[p], p))

        LOG.info("HPO information content initialized")

    def _get_term_frequencies(self, diseases, hpo):
        """Populate term frequencies"""
        raw_freq = defaultdict(float)

        for disease in diseases.diseases.values():
            for hp_term, freq in disease.phenotype_freqs.items():
                # Try to resolve term
                try:
                    term = hpo[hp_term]
                except KeyError:
                    continue

                prevalence = 1
                freq = 1
                raw_freq[term] += freq * prevalence

        # Normalize all frequencies to sum to 1
        term_freq = {}
        total_freq = sum(raw_freq.values())
        for term in raw_freq:
            assert term not in term_freq
            term_freq[term] = _bound(raw_freq[term] / total_freq)

        return term_freq

    def _get_descendant_lookup(self, root, accum=None):
        if accum is None:
            accum = {}
        if root in accum:
            return

        descendants = set([root])
        for child in root.children:
            self._get_descendant_lookup(child, accum)
            descendants.update(accum[child])
        accum[root] = descendants
        return accum

    def _get_ics(self, root, term_freq):
        term_descendants = self._get_descendant_lookup(root)

        term_ic = {}
        for node, descendants in term_descendants.items():
            prob_mass = 0.0
            for descendant in descendants:
                prob_mass += term_freq.get(descendant, 0)

            if prob_mass > EPS:
                prob_mass = _bound(prob_mass)
                term_ic[node] = -log(prob_mass)

        return term_ic

    def _get_link_strengths(self, root, term_ic):
        lss = {}

        # P(term&parents) = P(term|parents) P(parents)
        # P(term|parents) = P(term&parents) / P(parents)
        # P(parents) = probmass(descendants)
        for term, ic in term_ic.items():
            assert term not in lss
            if term.parents:
                max_parent_ic = max([term_ic[parent] for parent in term.parents])
                ls = max(ic - max_parent_ic, 0.0)
            else:
                ls = 0.0

            lss[term] = ls

        return lss

    def information_content(self, terms):
        """Return the information content of the given terms, without backoff"""
        return sum([self.term_ic.get(term, 0) for term in terms])


### END of Code required by the HPOIC class ###
