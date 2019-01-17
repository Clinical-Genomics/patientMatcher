# patientMatcher [![Build Status][travis-image]][travis-url] [![Coverage Status][coveralls-image]][coveralls-url]
A MatchMaker Exchange server

## Installation
Clone the repository from github using this command:
```bash
git clone https://github.com/Clinical-Genomics/patientMatcher.git
```

Change directory to the cloned folder and from there install the software using the following command:
```bash
pip install -e .
```

To run the app you either run the following command:
```bash
pmatcher run --host=host_address --port=port_number
```
(Leave blank host and port parameters to run the server with their default values -> host=127.0.0.1 and port=5000).

The recommended option is however to customise the parameters present in the configuration file (instance/config.py) and run the app using these parameters instead. To do so execute:
```bash
python run.py
```

## Patient matching algorithm
Each patient query submitted to the server via a POST request triggers a matching algorithm which will search and return those patients on the server that are most similar to the queried one.
Patient similarity is measured by the a **similarity score** that may span **from 0 (no matching) to 1 (exact matching)**.

Similarity score computation is taking into account **genomic similarity** and **phenotype similarity** across patients. The weight of these two factors is numerically evaluated into a GTscore and a PhenoScore, and the sum of the 2 constitutes the similarity score of the matching patient.

The relative weight of the GTscore and the PhenoScore can be customised by the database administrator by changing the values of the parameters "MAX_GT_SCORE" and "MAX_PHENO_SCORE" in the configuration file (instance/config.py). Default values are MAX_GT_SCORE: 0.75, MAX_PHENO_SCORE : 0.25.


### Genotyping matching algorithm
GTscore is computed by evaluating the list of genomic features of the queried patient and the patients available on the MME server.

If the queried patient has no genomic features (only phenotype features) then GTscore of all the returned matches will be 0.

Example of how the algorithm works:
Let's assume that 0.75 is the MAX_GT_SCORE possible for a patient match (default parameters).

If for instance the queried patient (QUERY) has 3 variants, **each variant will have a relative weight** of 0.25 (0.75/3). 0.25 will be the maximum score for each variant.
Assuming having a QUERY patient with these variants:
 - gene X variant A
 - gene Y variant B
 - gene Z variant C

Any patient in the database having variants in any of the X,Y,Z genes will constitute a match (MATCH) to the queried patient and will be compared against it.
Let's assume the variants in MATCH are:
- gene X variant D (1)
- gene Y variant B (2)
- gene W variant E (3)

The evaluation of the matching features is always performed on the QUERY variants, in this way:
- gene X variant A ---> gene match with (1). No variant match. Assigned score: 0.25/4 (gene match only will be arbitrarily assigned a fourth of the relative weight of the variant)
- gene Y variant B ---> exact matching of variant and gene with (2). Assigned score: 0.25 (max relative weight of the variant)
- gene Z variant C ---> No match, assigned score: 0.

GTscore assigned to the MATCH patients will then be: 0.25/4 + 0.25 + 0.

Note that the algorithm will evaluate and assign a score of 0.25 (max relative weight of the variant) also to matching variants outside genes.
This way patients will be evaluated for genetic similarity even if the variants lay outside genes.

[travis-url]: https://travis-ci.org/Clinical-Genomics/patientMatcher
[travis-image]: https://img.shields.io/travis/Clinical-Genomics/patientMatcher.svg?style=flat-square

[coveralls-url]: https://coveralls.io/github/Clinical-Genomics/patientMatcher?branch=master
[coveralls-image]: https://coveralls.io/repos/github/Clinical-Genomics/patientMatcher/badge.svg?branch=master
