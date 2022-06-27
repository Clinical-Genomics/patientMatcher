## Phenotype resources
Phenotype resources are used for matching patients based on phenotype features. These resources must be available whenever a server doesn't run in testing mode (`TESTING = False` in the app config file).

When the non-demo app server is lauched, it tries to download the following files:

- [HPO terms](https://raw.githubusercontent.com/obophenotype/human-phenotype-ontology/master/hp.obo)
- [Diagnoses](https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/misc/phenotype_annotation.tab)

The downloaded resources will be parsed and the available phenotype terms (HPO, OMIM, Decipher and Orphanet) will be used to build a model used for scoring the similarity between patients.

If the download of one or both files fails, then the server will try to use the same files available under patientMatcher/resources, provided together with the software, last time that it was installed. Note that files provided by the software are not guaranteed to be up-to-date with the latest definitions of HPO, OMIM, Decipher and Orphanet.

It is important that these resources are updated often (every few months or even better whenever a new version of the files above is available), since the availability of these terms has an impact on the phenotype scoring algorithm.

To update the resource files is it sufficient to restart a non-demo server.
