#!/usr/bin/env python

import os
import json
import re
import subprocess
import nibabel as nib
import codecs

# Things that this script checks
#
# * make sure tck has streamlines


with open('config.json') as config_json:
    config = json.load(config_json)

results = {"output": "", "errors": [], "warnings": []}

#TODO - how should I keep up wit this path?
mrinfo="/N/soft/rhel6/mrtrix/0.3.15/mrtrix3/release/bin/mrinfo"

directions = None


def validate_tck(config):
    # TODO - Not sure how to even validate tck files

    """
    print("running mrinfo")
    info = subprocess.check_output(["mrinfo", config], shell=False)
    results['t1_mrinfo'] = info  # deprecated
    results['mrinfo'] = info
    """
    config = str(config)
    track = codecs.open(config, "r",encoding='utf-8', errors='ignore')
    ls = track.readlines()[0:4]

    if int(ls[1].split()[1]) == 0:
        results['errors'].append('tck file has no streamlines!')

    s = ls[0].rstrip()
    for line in ls[1:4]:
        s += line.rstrip()

    results['output'] = s

validate_tck(config['track'])

with open("products.json", "w") as fp:
    json.dump([results], fp)

