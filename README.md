# patientMatcher
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
