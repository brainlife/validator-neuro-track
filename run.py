#!/usr/bin/env python

import os
import json
import re
import subprocess
import nibabel as nib

# Things that this script checks
# 
# * make sure mrinfo runs successfully on specified tck file
# * make sure tck has streamlines


with open('config.json') as config_json:
    config = json.load(config_json)

results = {"errors": [], "warnings": []}

#TODO - how should I keep up wit this path?
mrinfo="/N/soft/rhel6/mrtrix/0.3.15/mrtrix3/release/bin/mrinfo"

directions = None


def validate_tck(config):
    # TODO - Not sure how to even validate tck files
    try:

        print("running mrinfo")
        info = subprocess.check_output(["mrinfo", config], shell=False)
        results['t1_mrinfo'] = info  # deprecated
        results['mrinfo'] = info

        info_lines = info.split("\n")
        
        # check # of streamlines
        tck = nib.streamlines.load(config)
        tg = tck.tractogram
        streamlines = tg.streamlines
        if len(streamlines) == 0:
            results['errors'].append('tck file has no streamlines!')

    except subprocess.CalledProcessError as err:
        results['errors'].append("mrinfo failed on tck. error code: " + str(err.returncode))

validate_tck(config['track'])

with open("products.json", "w") as fp:
    json.dump([results], fp)