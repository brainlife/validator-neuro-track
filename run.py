#!/usr/bin/python3 -u

import os
import json
import numpy as np
import nibabel as nib
from dipy.viz import window, actor
from xvfbwrapper import Xvfb
import base64
import itertools

with open('config.json') as config_json:
    config = json.load(config_json)

if not os.path.exists("output"):
    os.mkdir("output")

if os.path.lexists("output/track.tck"):
    os.remove("output/track.tck")
os.symlink("../"+config['track'], "output/track.tck")

# start virtual display
print("starting Xvfb");
vdisplay = Xvfb()
vdisplay.start()

results = {"errors": [], "warnings": [], "meta": {}}

print("loading track")
track = nib.streamlines.load(config["track"], lazy_load=True)
results["meta"] = track.header

print("sampling streamlines")
streamlines = list(itertools.islice(track.streamlines, 50000))

print("streamlines into visualizer")
stream_actor = actor.line(streamlines)

#print(track.header)
results["meta"]["_dtype"] = str(results["meta"]["_dtype"])
results["meta"]["magic_number"] = str(results["meta"]["magic_number"])
results["meta"]["voxel_to_rasmm"] = results["meta"]["voxel_to_rasmm"].tolist()
print(results["meta"])

# set camera position
# need to add check for advanced input camera positions, focal points, viewup, and views: TODOLATER
camera_pos = [(-5.58, 84.98, 467.47), (-482.32, 3.58, -6.28),
              (-7.65, 421.00, -173.05), (455.46, 9.14, 95.68)]
focal_point = [(-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47),
               (-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47)]
view_up = [(0.00, 1.00, -0.21), (0.00, 0.00, 1.00),
              (0.00, 0.00, 0.05), (0.00, 0.00, 1.00)]

# set slice view names
views = ['axial', 'sagittal_left', 'coronal', 'sagittal_right']

# set renderer window
renderer = window.Renderer()

# add streamlines to renderer
renderer.add(stream_actor)

if not os.path.exists("secondary"):
    os.mkdir("secondary")

results["brainlife"] = []

# for loops through views
for v in range(len(views)):
    print("creating image with %s orientation" %views[v])

    # set camera view
    renderer.set_camera(position=camera_pos[v],
            focal_point=focal_point[v],
            view_up=view_up[v])

    # save pngs
    print("Creating tractogram png of view %s" %views[v])
    out_name = 'secondary/'+views[v]+'.png'
    window.record(renderer,out_path=out_name,size=(600,600),reset_camera=False)

    encoded = base64.b64encode(open(out_name, "rb").read()).decode('utf-8')
    if views[v] == "sagittal_left":
        results["brainlife"].append({ "type": "image/png", "name": views[v], "base64": encoded, "desc": "50k samples"})

    # append information for file list for json output
    #temp_dict = {}
    #temp_dict["filename"]='secondary/tractogram_'+views[v]+'.png'
    #temp_dict["name"]='Tractogram '+views[v].replace('_', ' ') + ' view'
    #temp_dict["desc"]= 'This figure shows the '+views[v].replace('_', ' ') + ' view of the tractogram'
    #file_list.append(temp_dict)

    print("%s orientation complete" %views[v])

vdisplay.stop()

results["meta"]["validator_version"] = "1.0";

with open("product.json", "w") as fp:
    json.dump(results, fp)

