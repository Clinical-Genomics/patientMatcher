## [3.1.1] - 2022-01-15
### Fixed
- Parsing of numerical and boolean env vars when creating the app

## [3.1] - 2022-01-13
### Changed
- Speed-up CI tests by caching installation of libs and splitting tests into randomized groups using pytest-test-groups
- Mock Ensembl services (gene conversions and liftover) used all tests
- Mock the download of files containing phenotype resources in tests

## [3.0] - 2021-12-27
### added
- Index (landing page) reachable at endpoint `/`
- Include software version in matching emails body
### Fixed
- Restore saving of all matching attempts into database, also those with no results
- Parsing of admins emails list when provided using env vars
- Heartbeat endpoint to return True or False if the app is prod or staging app
### Changed
- Refactor command line params and options to be compliant with the GNU coding standards

## [2.13] - 2021-12-13
### added
- GitHub action to push staging branches from pull requests to Docker Hub
- Created another Dockerfile to run the app via Gunicorn
- Modified  GitHub actions to push Dockerfile-server image (stage) to Docker Hub when a pull request is opened or modified
### Changed
- Docker base image to run the app via Docker and Gunicorn in a prod environment
- Created another Dockerfile to run the app via Gunicorn
- Extended config file functionality to collect all required params from environment variables
- Modified README to describe the two distinct Dockerfiles
- Modified the docker-compose to provide an example on how to use the two Dockerfiles
- Modified  GitHub actions to push both Dockerfile and Dockerfile-server images (prod) to Docker Hub when a new release is created
- Improved initial debug messages reporting database connection info
### Fixed
- Freeze PyMongo lib to version<4.0 to keep supporting previous MongoDB versions
- Deprecated werkzeug.contrib preventing running the docker app in prod environment

## [2.12] - 2021-11-24
### Fixed
- Removed unused imports
### added
- Vulture GitHub action to flag unused code with 90% confidence
### Changed
- Scan only changed files with Vulture action

## [2.11] - 2021-11-16
### Fixed
- Fix some deprecated code causing warnings during automatic tests
- Do not duplicate `mailto` schema when contact href is an email with correct schema
### Changed
- Improve views code by reusing a controllers function when request auth fails
### Added
- Bulk replace patients' contact info using the command line
- Documentation on how to update patients' contact info using the command line
- Contact href string validation (schemas: http, https, mailto) when saving or updating patients

## [2.10.2] - 2021-11-12
### Fixed
- Increase MongoDB connection serverSelectionTimeoutMS to 30K (default value according to MongoDB documentation)

## [2.10.1] - 2021-10-12
### Fixed
- Params passed from the command line to the custom FlaskGroup

## [2.10] - 2021-10-12
### Added
- Software purpose and short description of developers and Stockholm MME node in README
### Changed
- Improve docker-compose file with 2 demo connected nodes
- Replaced vepo/mongo with the official MongoDB image mongo:4.4.9 in docker-compose files
- Created a mongo-init script for database authentication in docker-compose `docker-compose_auth_server_with_2_nodes.yml` development file
- Modified docker-compose file to connect to database without authentication
- Modified the `pytest_codecov` GitHub action file to connect to database  matrix (MongoDB 3.2, 4.4, 5.0) without authentication
- Some cli commands don't instantiate a complete app object
- Fixed the code to connect to a MongoDB replica set
### Fixed
- Removed unused `--ensembl_genes` parameter from `add demodata` command in all docker-compose file

## [2.9] - 2021-09-22
### Added
### Changed
- Save Ensembl ids for demo patient data genes automatically
- Mock the Ensembl REST API converting gene symbols to Ensembl IDs in tests
- Changed the tests for the gene conversion Ensembl APIs to use mocks APIs
- Do not download resources when testing the update resources command
- Use the requests lib instead of urllib.request to interrogate the Ensembl APIs
- Split cli tests into 4 dedicated files (test_add, test_remove, test_update, test_commands)
### Fixed
- Syntax in the disclaimer
- Validate the Ensembl gene ID against the Ensembl API when multiple IDs are returned by converting a HGNC symbol.

## [2.8] - 2021-09-17
### Added
- .cff citation file and doi badge on readme page
- GitHub action to publish repo to PyPI when a new release is created
### Changed
### Fixed
- Fixed in README file the server port used by the web server container launched from docker-compose
- Provide a content type description for long_description in setup file

## [2.7] - 2021-09-07
### Added
- A demo docker-compose file with a MME server connected to 2 other nodes under `/containers`
### Changed
### Fixed
- Assign 2 different ids to the demo connected nodes in docker-compose

## [2.6] - 2021-08-11
### Added
- Email logging of errors howto in readme
- Inclusive-language check using [woke](https://github.com/get-woke/woke) github action
### Changed
- Removed coveralls badge and added codecov badge
- Required downloading of hp.obo.txt and phenotype_annotation.tab.txt to run a non-test app
- Integrate HPO parsing and handling into the software (decouple from Patient-similarity for HPO)
- Integrate OMIM parsing and handling into the software (decouple from Patient-similarity for OMIM)
- Use app port 9020 instead of 5000 in docker-compose
- Use MongoDB port 27013 instead of 27017 in docker-compose
- Subnet address used in bridge of docker-compose file
- Integrate HPOIC (HPO info content) creation in HPO extensions (decouple from Patient-similarity for HPOIC)
- All collections are removed and recreated on `add demodata` rerun
- Demo client with token `DEMO` is created when `add demodata` command is run
- Remove patient-similarity dependency and replace needed functions with internal code
### Fixed
- downloading phenotype_annotation.tab file from Monarch Initiative
- document keys when a demo client is created with the command `pmatcher add demodata`

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
