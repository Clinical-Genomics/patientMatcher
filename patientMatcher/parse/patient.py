# -*- coding: utf-8 -*-

def mme_patient(json_patient):
    """
        Accepts a json patient and converts it to a MME patient,
        formatted as required by patientMatcher database

        Args:
            patient_obj(dict): a patient object as in https://github.com/ga4gh/mme-apis

        Returns:
            mme_patient(dict) : a mme patient entity
    """

    # fix patient's features:
    for feature in json_patient.get('features'):
        feature['_id'] = feature.get('id')
        feature.pop('id')

    mme_patient = {
        '_id' : json_patient['id'],
        'label' : json_patient.get('label'),
        'contact' : json_patient['contact'],
        'features' : json_patient['features'],
        'genomicFeatures' : json_patient.get('genomicFeatures'),
        'disorders' : json_patient.get('disorders'),
        'species' : json_patient.get('species'),
        'ageOfOnset' : json_patient.get('ageOfOnset'),
        'inheritanceMode' : json_patient.get('inheritanceMode')
    }
    return mme_patient
