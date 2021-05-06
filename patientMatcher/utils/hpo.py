# -*- coding: utf-8 -*-
import logging

from patientMatcher.resources import path_to_hpo_terms

LOG = logging.getLogger(__name__)

ROOT = "HP:0000001"


class HPNode(object):
    """Populate an HPO object node from a list of lines in the HPO intology file"""

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

    def is_root(self):
        """returns True if node is root"""
        return self.id == ROOT

    def validate(self):
        """Make sure a node has an ID, a name and parents (if node is not root)"""
        return bool(self.id) and bool(self.name) and self.obsolete is False

    def link(self, hps):
        """Link a node objects to its parents and children on the ontology tree"""
        for hp in self._parent_hps:
            parent = hps.get(hp)
            self.parents.add(parent)
            parent.children.add(self)


class HPO(object):
    """Parse and HPO ontology to make it available for phenotype matching"""

    def init_app(self, app):
        """Initialize the HPO ontology when the app is launched."""
        self.root = ROOT
        self.hps = {}
        self.parse_ontolology()

    def parse_ontolology(self):
        """Parse HPO ontology file, that is available under patientMatcher/resources"""
        with open(path_to_hpo_terms, encoding="utf-8") as hpofile:
            counter = 0
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

                    hpo_lines = []  # Reset lines for next HPO term
                    continue
                hpo_lines.append(line)

        # Connect HP objects in a tree
        nodes = set(self.hps.values())

        for node in nodes:
            node.link(self.hps)

        LOG.info(f"Parsed {len(nodes)} HP terms into HPO nodes from resource file")
