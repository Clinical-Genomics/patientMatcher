# -*- coding: utf-8 -*-
import patientMatcher.utils.ensembl_rest_client as ensembl_client


def liftover(build, chrom, start, end):
    """Perform variant liftover using Ensembl REST API

    Accepts:
        build(str): genome build: GRCh37 or GRCh38
        chrom(str): 1-22,X,Y,MT
        start(int): start coordinate
        stop(int): stop coordinate

    Returns
        mappings(list of dict): example: [{
            "end": 1039365,
            "seq_region_name": "X",
            "coord_system": "chromosome",
            "assembly": "GRCh38",
            "start": 1039265,
            "strand": 1
          }]
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
            f"{chrom}:{start}..{end}",
            f"{assembly2}?content-type=application/json",
        ]
    )
    result = client.send_request(url)
    if isinstance(result, dict):
        return result.get("mappings")
