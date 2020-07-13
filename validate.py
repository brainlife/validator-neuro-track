#!/usr/bin/python3 -u


from fury import actor, window
from fury.optpkg import optional_package
from PIL import Image


import itertools
import json
import nibabel as nib
import os


xvfbwrapper, has_xvfbwrapper, setup_module = optional_package('xvfbwrapper')
if has_xvfbwrapper:
    from xvfbwrapper import Xvfb


_VIEW_PARAMS = [{'view': 'axial', 'cam_pos': (-5.58, 84.98, 467.47),
                 'focal_pnt': (-8.92, -16.15, 4.47),
                 'view_up': (0.00, 1.00, -0.21)},

                {'view': 'sagittal_left', 'cam_pos': (-482.32, 3.58, -6.28),
                 'focal_pnt': (-8.92, -16.15, 4.47),
                 'view_up': (0.00, 0.00, 1.00)},

                {'view': 'coronal', 'cam_pos': (-7.65, 421.00, -173.05),
                 'focal_pnt': (-8.92, -16.15, 4.47),
                 'view_up': (0.00, 0.00, 0.05)},

                {'view': 'sagittal_right', 'cam_pos': (455.46, 9.14, 95.68),
                 'focal_pnt': (-8.92, -16.15, 4.47),
                 'view_up': (0.00, 0.00, 1.00)}]


def add_header_properties(dictionary, header, parent_key='meta'):
    """
    Extracts some keys of the header and puts them in a dictionary.

    :param dictionary: Python dictionary.
    :param header: Dict-like structure.
    :param parent_key: (String) Key label for the dictionary.
    :return: Transformed dictionary with the new keys.
    """
    dictionary[parent_key] = header
    dictionary[parent_key]['_dtype'] = str(header.get('_dtype'))
    dictionary[parent_key]['magic_number'] = str(header.get('magic_number'))
    vox2rasmm = header.get('voxel_to_rasmm')
    if vox2rasmm is not None:
        dictionary[parent_key]['voxel_to_rasmm'] = vox2rasmm.tolist()
    else:
        dictionary[parent_key]['voxel_to_rasmm'] = str(vox2rasmm)
    return dictionary


def save_default_imgs(size=(500, 500), ext='jpg'):
    """
    Function to save view images when the input file does NOT fulfill the
    requirements of the validator.

    :param size: A 2-tuple, containing (width, height) in pixels.
    :param ext: (String) Extension of the output files.
    """
    img = Image.new('RGB', size=size, color='gray')
    for param in _VIEW_PARAMS:
        out_file = os.path.join('secondary', param['view'] + '.' + ext)
        print('Saving: {}'.format(out_file))
        img.save(out_file)


def save_views_imgs(lines, size=(500, 500), interactive=True, ext='jpg'):
    """
    Function to save view images when the input file does fulfill the
    requirements of the validator.

    :param lines: Streamlines-like object.
    :param size: A 2-tuple, containing (width, height) in pixels.
    :param interactive: (Boolean) If True, launches a window. Useful for
    developing/debugging options.
    :param ext: (String) Extension of the output files.
    """
    # Start virtual display
    if has_xvfbwrapper:
        print('Starting Xvfb')
        vdisplay = Xvfb()
        vdisplay.start()

    # Create streamlines actor
    streamlines_actor = actor.line(lines)

    # Set renderer window
    scene = window.Scene()

    # Add streamlines to renderer
    scene.add(streamlines_actor)

    # Loop through views
    for param in _VIEW_PARAMS:
        # Set camera
        scene.set_camera(position=param['cam_pos'],
                         focal_point=param['focal_pnt'],
                         view_up=param['view_up'])
        if interactive:
            window.show(scene, size=size)
        # Save imgs
        out_file = os.path.join('secondary', param['view'] + '.' + ext)
        print('Saving: {}'.format(out_file))
        window.record(scene, out_path=out_file, size=size)

    # Stop virtual display
    if has_xvfbwrapper:
        vdisplay.stop()


if __name__ == '__main__':
    # Read Brainlife's config.json
    with open('config.json', encoding='utf-8') as config_json:
        config = json.load(config_json)
    input_file = config['track']

    # Get extension, so validator can manipulate .tck and .trk files
    _, ext = os.path.splitext(input_file)

    # Create Brainlife's output dirs if don't exist
    if not os.path.exists('output'):
        os.mkdir('output')
    if not os.path.exists('secondary'):
        os.mkdir('secondary')

    # Brainlife setup of input file
    # Delete output symlink if doesn't exist
    symlink_fname = os.path.join('output', 'track' + ext)
    if os.path.lexists(symlink_fname):
        os.remove(symlink_fname)
    # Create symlink in `output` pointing to the input file
    os.symlink('../' + input_file, symlink_fname)

    # Initialize results dict
    results = {'errors': [], 'warnings': [], 'meta': {}}

    # Input file management
    # Load file
    print('Loading track file...')
    track = nib.streamlines.load(input_file, lazy_load=True)
    # Get input file's header
    header = track.header

    num_fibers = header.get('count')
    if num_fibers:
        # if len(track.streamlines) != track.header["count"]:
        #    results["errors"].append("tck header count doesn't match actual fiber counts")
        num_fibers = int(num_fibers)
        if num_fibers == 0:
            results['warnings'].append('Fiber count is 0.')
            save_default_imgs()
        else:
            # Generate snapshots
            # To reduce the memory and wall time we need to subsample the
            # streamline to show
            print('Sampling streamlines')
            samples = list(itertools.islice(track.streamlines, 50000))
            save_views_imgs(samples, interactive=True)
    else:
        results['errors'].append('`count` key not available in header.')
        save_default_imgs()

    # We should rely on service_branch associated with datasetproduct
    # results['meta']['validator_version'] = '1.0'

    results = add_header_properties(results, header)
    print(results)

    with open('product.json', 'w') as fp:
        json.dump(results, fp)
