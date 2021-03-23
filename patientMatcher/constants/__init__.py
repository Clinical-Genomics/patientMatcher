from patientMatcher.resources import path_to_hpo_terms, path_to_phenotype_annotations

# useful HTTP response status codes with messages
STATUS_CODES = {
    200: {"status_code": 200},
    400: {"message": "Invalid request JSON"},
    422: {"message": "Request does not conform to API specifications"},
    401: {"message": "Not authorized"},
    500: {"message": "An error occurred while updating the database"},
}

# phenotype terms and annotations are used by phenotype scoring algorithm and
# are updated using the CLI
PHENOTYPE_TERMS = {
    "hpo_ontology": {
        "url": "http://purl.obolibrary.org/obo/hp.obo",
        "resource_path": path_to_hpo_terms,
    },
    "hpo_annotations": {
        "url": "https://ci.monarchinitiative.org/view/hpo/job/hpo.annotations/lastSuccessfulBuild/artifact/rare-diseases/misc/phenotype_annotation.tab",
        "resource_path": path_to_phenotype_annotations,
    },
}
