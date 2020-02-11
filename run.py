#!/usr/bin/env python

import os
import json
import re
import subprocess
import nibabel as nib
import codecs

with open('config.json') as config_json:
    config = json.load(config_json)

results = {"headers": {}, "errors": [], "warnings": []}

directions = None

#track = codecs.open(config, "r",encoding='utf-8', errors='ignore')
with open(config['track']) as f:
    linenum=-1
    for line in f:
        line = line.strip()
        linenum+=1

        #reached end?
        if line == "END":
            break

        #first line should be "mrtrix tracks"
        if linenum == 0:
            if line != "mrtrix tracks":
                results['errors'].append('not mrtrix tracks')
            else:
                continue

        #print linenum, line
        tokens = line.split(":")
        k=tokens[0].strip()
        v=tokens[1].strip()
        results['headers'][k] = v

        if k == "count" and v == "0":
            results['errors'].append('tck file has no streamlines!')

if not os.path.exists("output"):
    os.mkdir("output")

#TODO - normalize
if os.path.lexists("output/track.tck"):
    os.remove("output/track.tck")
os.symlink("../"+config['track'], "output/track.tck")

#products.json is deprecated (exists for backward compatibility)
#with open("products.json", "w") as fp:
#    json.dump([results], fp)

with open("product.json", "w") as fp:
    json.dump(results, fp)


