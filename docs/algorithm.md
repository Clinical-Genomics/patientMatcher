## Patient matching algorithm.
Each patient query submitted to the server triggers a matching algorithm which will search and return those patients on the server that are most similar to the queried one.
Patient similarity is measured by the a **similarity score** that may span **from 0 (no matching) to 1 (exact matching)**.

Similarity score computation is taking into account **genomic similarity** and **phenotype similarity** across patients. The weight of these two factors is numerically evaluated into a GTscore and a PhenoScore, and the sum of the 2 constitutes the similarity score of the matching patient.

The relative weight of the GTscore and the PhenoScore can be customised by the database administrator by changing the values of the parameters "MAX_GT_SCORE" and "MAX_PHENO_SCORE" in the configuration file (instance/config.py). Default values are MAX_GT_SCORE: 0.5, MAX_PHENO_SCORE : 0.5.

<a name="geno_matching"></a>
### Genotyping matching algorithm
GTscore is computed by evaluating the list of genomic features of the queried patient and the patients available on the MME server. **PatientMatcher patients are saved with gene ids described by Ensembl gene ids**, but it's possible to search the database using patients with genes represented by HGNC symbols, Entrez ids and Ensembl ids.

If the queried patient has no genomic features (only phenotype features) then GTscore of all the returned matches will be 0.

Example of how the algorithm works:
Let's assume that 0.5 is the MAX_GT_SCORE possible for a patient match (default parameters).

If for instance the queried patient (QUERY) has 3 variants, **each variant will have a relative weight** of 0.1666 (0.5/3). 0.1666 will be the maximum score for each variant.
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
- gene X variant A ---> gene match with (1). No variant match. Assigned score: 0.1666/4 (gene match only will be arbitrarily assigned a fourth of the relative weight of the variant)
- gene Y variant B ---> exact matching of variant and gene with (2). Assigned score: 0.1666 (max relative weight of the variant)
- gene Z variant C ---> No match, assigned score: 0.

GTscore assigned to the MATCH patients will then be: 0.1666/4 + 0.1666 + 0.

Note that the algorithm will evaluate and assign a score of 0.1666 (max relative weight of the variant) also to matching variants outside genes.
This way patients will be evaluated for genetic similarity even if the variants lay outside genes.


<a name="pheno_matching"></a>
### Phenotype matching algorithm
Phenotype similarity is calculated by taking into account **features and disorders** of a patient.

- **Patient features**
are specified by the eventual HPO terms provided for the query patient. **Similarity between HPO features will be equal the maximum similarity score** between two patients **if no disorders (OMIM terms) are provided** for one or both patients.   
**Otherwise feature similarity score will make up 1/2 of the maximum similarity score**.
Feature similarity is calculated as the simgic score obtained by comparing HPO terms of a query patient with those from a matching patient.
You can find more information on semantic similarity comparison algorithms in [this paper](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-9-S5-S4)

- **Disorders**
(OMIM diagnoses), if available, will make up **1/2 of the maximum similarity score**. OMIM score is calculated by pairwise comparison of the available OMIM terms for the patients.
&nbsp;
