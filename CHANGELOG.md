## [] -
### Changed
- Pulling Docker images in docker-compose from clinicalgenomics Docker Hub

### Added
- Display error message and raise exception when Ensembl Rest API is needed but offline
- New Dockerfile and instructions to run on docker


## [2.2] - 2020-10-19

### Added
- Codeowners document

### Fixed
- Avoid pymongo-related deprecated code
- Unblock pytest and mongomock dependencies


## [2.1]

### Modified
- Open up metrics endpoint for any request (no token needed)

### Fixed
- Update HPO file name to reflect resource on compbio.charite.de/jenkins


## [2.0] - 2019-11-17

### Modified
- Ensembl gene IDs to describe gene IDs
- Allow matching when external patients have entrez gene IDs or HGNC symbols
- Display contact email in notification emails
- Save to database only matches with results or error messages


## [1.4] - 2019-11-06

### Modified
- Allow gene search using ensembl gene IDs



## [1.3] - 2019-10-31

### Fixed
- Handle better external matching errors
- Fix a bug introduced in version 1.2.0 (missing patient id in results)



## [1.2.1] - 2019-10-30

### Modified
- Remove Host from external request headers for compatibility issues



## [1.2.0] - 2019-10-29

### Added
- Introduced SCORE_THRESHOLD parameter as a minimum patient score threshold for returned results

### Modified
- Command line returns app version



## [1.1.1] - 2019-04-25

### Modified
-  Fixed bug in phenotype matching when no OMIM or no HPO terms are available



## [1.1.0] - 2019-04-25

### Modified
-  patient-similarity against all patients in database if query patient has HPO term



## [1.0.0] - 2019-04-18

### Added
-  patient-similarity integration for phenotype scoring
