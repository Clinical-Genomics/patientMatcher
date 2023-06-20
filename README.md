# patientMatcher - a Python and MongoDB - based MatchMaker Exchange server
![Build Status - GitHub][actions-build-status]
[![DOI](https://zenodo.org/badge/DOI/10.1002/humu.24358.svg)](https://doi.org/10.1002/humu.24358)


PatientMatcher is a **Python** (Flask) and **MongoDB** - based implementation of a [MatchMaker Exchange](https://www.matchmakerexchange.org/) (MME) server, developed and actively maintained by [Clinical Genomics, Science For Life Laboratory in Stockholm](https://www.scilifelab.se/units/clinical-genomics-stockholm/). PatientMatcher is designed as a standalone application, but can easily communicate with external applications via REST API. The MME Stockholm node is being implemented in clinical production in collaboration with the Genomic Medicine Center Karolinska at the Karolinska University Hospital.    

Info on how to test PatientMatcher or to set up a server containing an app frontend and backend is available on the [documentation pages](https://clinical-genomics.github.io/patientMatcher).


[actions-build-status]: https://github.com/Clinical-Genomics/patientMatcher/actions/workflows/docker_build_n_publish_stage.yml/badge.svg