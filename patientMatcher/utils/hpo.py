# -*- coding: utf-8 -*-
import logging
from collections import defaultdict

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

        LOG.info("HPO information content initialized")

    def _get_term_frequencies(self, diseases, hpo):

        raw_freq = defaultdict(float)

        for id, disease in diseases.diseases.items():
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

        # Normalize all frequencies to sum to 1
        term_freq = {}
        total_freq = sum(raw_freq.values())
        for term in raw_freq:
            assert term not in term_freq
            term_freq[term] = _bound(raw_freq[term] / total_freq)

        return term_freq


#    dev __init__():
