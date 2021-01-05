# -*- coding: utf-8 -*-
import patientMatcher.utils.ensembl_rest_client as ensembl_client


def liftover(build, chrom, start, end=None):
    """Perform variant liftover using Ensembl REST API

    Accepts:
        build(str): genome build: GRCh37 or GRCh38
        chrom(str): 1-22,X,Y,MT
        start(int): start coordinate
        stop(int): stop coordinate or None

    Returns
        mappings(list of dict):
            example: https://rest.ensembl.org/map/human/GRCh37/X:1000000..1000100:1/GRCh38?content-type=application/json
    """
    assembly2 = "GRCh38"
    if build == "GRCh38":
        assembly2 = "GRCh37"

    client = ensembl_client.EnsemblRestApiClient()
    url = "/".join(
        [
            client.server,
            "map/human",
            build,
            f"{chrom}:{start}..{end or start}",  # End variant provided is not required
            f"{assembly2}?content-type=application/json",
        ]
    )
    result = client.send_request(url)
    if isinstance(result, dict):
        return result.get("mappings")
