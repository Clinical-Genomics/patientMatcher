import pkg_resources

###### Files ######
hpo_filename = 'resources/hp.obo.txt'
phenotype_annotation_filename = 'resources/phenotype_annotation.tab.txt'
benchmark_patients = 'resources/benchmark_patients.json'
json_api ='resources/api.json'

###### Paths ######
path_to_hpo_terms = pkg_resources.resource_filename('patientMatcher',
    hpo_filename)

path_to_phenotype_annotations = pkg_resources.resource_filename('patientMatcher',
    phenotype_annotation_filename)

path_to_benchmark_patients = pkg_resources.resource_filename('patientMatcher',
    benchmark_patients)

path_to_json_api = pkg_resources.resource_filename('patientMatcher', json_api)
