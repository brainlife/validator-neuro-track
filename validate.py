#!/usr/bin/python3 -u

import os
import json
import numpy as np
import nibabel as nib
from dipy.viz import window, actor
from xvfbwrapper import Xvfb
import base64
import itertools
from PIL import Image

with open('config.json', encoding='utf-8') as config_json:
    config = json.load(config_json)

if not os.path.exists("output"):
    os.mkdir("output")
if not os.path.exists("secondary"):
    os.mkdir("secondary")

if os.path.lexists("output/track.tck"):
    os.remove("output/track.tck")
os.symlink("../"+config['track'], "output/track.tck")

results = {"errors": [], "warnings": [], "meta": {}}

print("loading tck..")
track = nib.streamlines.load(config["track"], lazy_load=True)

#if len(track.streamlines) != track.header["count"]:
#    results["errors"].append("tck header count doesn't match actual fiber counts")

views = ['axial', 'sagittal_left', 'coronal', 'sagittal_right']

if int(track.header["count"]) == 0:
    results["warnings"].append("fiber count is 0")

    img = Image.new('RGB', (500, 500), color='gray')
    for v in range(len(views)):
        img.save('secondary/'+views[v]+'.jpg')
else:
    #generate snapshot!

    #to reduce the memory and walltime, we need to sub-sample the streamlines to show
    print("sampling streamlines")
    samples = list(itertools.islice(track.streamlines, 50000))

    print("streamlines into visualizer")
    stream_actor = actor.line(samples)

    # set camera position
    # need to add check for advanced input camera positions, focal points, viewup, and views: TODOLATER
    camera_pos = [(-5.58, 84.98, 467.47), (-482.32, 3.58, -6.28),
                  (-7.65, 421.00, -173.05), (455.46, 9.14, 95.68)]
    focal_point = [(-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47),
                   (-8.92, -16.15, 4.47), (-8.92, -16.15, 4.47)]
    view_up = [(0.00, 1.00, -0.21), (0.00, 0.00, 1.00),
                  (0.00, 0.00, 0.05), (0.00, 0.00, 1.00)]


    # start virtual display
    print("starting Xvfb");
    vdisplay = Xvfb()
    vdisplay.start()

    # set renderer window
    renderer = window.Renderer()

    # add streamlines to renderer
    renderer.add(stream_actor)

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
        out_name = 'secondary/'+views[v]+'.jpg'
        #window.record(renderer,out_path=out_name,size=(700,700),reset_camera=False)
        window.record(renderer,out_path=out_name,size=(500,500))

        #encoded = base64.b64encode(open(out_name, "rb").read()).decode('utf-8')

        #print("%s orientation complete" %views[v])

    vdisplay.stop()

#we should rely on service_branch associated with datasetproduct
#results["meta"]["validator_version"] = "1.0";

results["meta"] = track.header

#make some header json serializable
results["meta"]["_dtype"] = str(results["meta"]["_dtype"])
results["meta"]["magic_number"] = str(results["meta"]["magic_number"])
results["meta"]["voxel_to_rasmm"] = results["meta"]["voxel_to_rasmm"].tolist()
print(results)

with open("product.json", "w") as fp:
    json.dump(results, fp)

