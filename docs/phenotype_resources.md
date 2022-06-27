## Phenotype resources
Phenotype resources are used for matching patients based on phenotype features. These resources must be available whenever a server doesn't run in testing mode (`TESTING = False` in app config file).

When the non-demo app server is lauched, it tries to download the following files:

- [HPO terms](https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo)
- [Diagnoses](https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/misc/phenotype_annotation.tab)

These files will be parsed and the available phenotype terms (HPO, OMIM, Decipher and Orphanet) will be used to build a model used for scoring the similarity between patients.

It is important that these resources are updated often (evrry few months or whenever a new version of the files above is released), since the availability of these terms is affecting the phenotype scoring algorithm.

To update the resource files is it sufficient to restart a non-demo server once in a while
