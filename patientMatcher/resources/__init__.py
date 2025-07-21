from importlib.resources import files

###### Files ######
hpo_filename = "resources/hp.obo.txt"
phenotype_annotation_filename = "resources/phenotype.hpoa"
benchmark_patients = "resources/benchmark_patients.json"
json_api = "resources/api.json"

###### Paths ######
base = files("patientMatcher")

path_to_hpo_terms = str(base.joinpath(hpo_filename))
path_to_phenotype_annotations = str(base.joinpath(phenotype_annotation_filename))
path_to_benchmark_patients = str(base.joinpath(benchmark_patients))
path_to_json_api = str(base.joinpath(json_api))
