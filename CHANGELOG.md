## [] -
### Added
- Email logging of errors howto in readme
- Inclusive-language check using [woke](https://github.com/get-woke/woke) github action
### Changed
- Removed coveralls badge and added codecov badge
- Required downloading of hp.obo.txt and phenotype_annotation.tab.txt to run a non-test app
- Integrate HPO parsing and handling into the software (decouple from Patient-similarity for HPO)
- Integrate OMIM parsing and handling into the software (decouple from Patient-similarity for OMIM)
### Fixed
- downloading phenotype_annotation.tab file from Monarch Initiative


## [2.5] - 2021-01-20
### Added
- Notify admins via email when app crashes
### Changed
- Use codecov instead of coveralls in github actions
- Send notification emails using TLS instead of SSL
### Fixed

## [2.4.1] - 2021-01-07
### Added
### Changed
### Fixed
- Liftover crashing when no end coordinate is not provided

## [2.4] - 2020-12-30
### Added
- Code for performing coordinate liftover using Ensembl REST API
- Variant liftover when comparing genotype features
### Changed
- Using coloredlogs for app logs
### Fixed
- removed unused docker folder

## [2.3.1] - 2020-12-04
### Added
### Changed
- Install requirements in setup
- Improved Dockerfile and docker-compose files
### Fixed
- Connection string to database when creating the app

## [2.3] - 2020-12-01
### Changed
- Pulling Docker images in docker-compose from clinicalgenomics Docker Hub
- Switched from Travis CI to github actions

### Changed
- Display error message and raise exception when Ensembl Rest API is needed but offline
- New Dockerfile and instructions to run on docker
- Github action to build and push Docker image when a new software release is created
- Try to match patients based on gene symbol (gene._geneName) if gene.id doesn't match

### Fixed
- Do not crash trying to convert genes when Ensembl REST API isn't available


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
