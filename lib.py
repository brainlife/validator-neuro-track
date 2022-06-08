# TODO wait new VTK release to handle multiple clients exception
# TODO look for VTK API to clear up clients
# More info at https://github.com/pyvista/pyvista/issues/1180

import vtkmodules.vtkRenderingCore as rcvtk
import vtkmodules.vtkFiltersHybrid as fhvtk
from vtkmodules.util import numpy_support
from fury.window import enable_stereo, save_image

RenderWindow = rcvtk.vtkRenderWindow
RenderWindowInteractor = rcvtk.vtkRenderWindowInteractor
RenderLargeImage = fhvtk.vtkRenderLargeImage

renWin = RenderWindow()
iren = RenderWindowInteractor()
iren.SetRenderWindow(renWin)

def close():
    iren.TerminateApp()
    renWin.Finalize()


# https://github.com/fury-gl/fury/blob/master/fury/window.py#L674
def record(scene, cam_pos=None, cam_focal=None, cam_view=None,
           out_path=None, path_numbering=False, n_frames=1, az_ang=10,
           magnification=1, size=(300, 300), reset_camera=True,
           screen_clip=False, stereo='off', verbose=False):
    """Record a video of your scene.
    Records a video as a series of ``.png`` files of your scene by rotating the
    azimuth angle az_angle in every frame.
    Parameters
    -----------
    scene : Scene() or vtkRenderer() object
        Scene instance
    cam_pos : None or sequence (3,), optional
        Camera's position. If None then default camera's position is used.
    cam_focal : None or sequence (3,), optional
        Camera's focal point. If None then default camera's focal point is
        used.
    cam_view : None or sequence (3,), optional
        Camera's view up direction. If None then default camera's view up
        vector is used.
    out_path : str, optional
        Output path for the frames. If None a default fury.png is created.
    path_numbering : bool
        When recording it changes out_path to out_path + str(frame number)
    n_frames : int, optional
        Number of frames to save, default 1
    az_ang : float, optional
        Azimuthal angle of camera rotation.
    magnification : int, optional
        How much to magnify the saved frame. Default is 1.
    size : (int, int)
        ``(width, height)`` of the window. Default is (300, 300).
    screen_clip: bool
        Clip the the png based on screen resolution. Default is False.
    reset_camera : bool
        If True Call ``scene.reset_camera()``. Otherwise you need to set the
         camera before calling this function.
    stereo: string
        Set the stereo type. Default is 'off'. Other types include:
        * 'opengl': OpenGL frame-sequential stereo. Referred to as
          'CrystalEyes' by VTK.
        * 'anaglyph': For use with red/blue glasses. See VTK docs to
          use different colors.
        * 'interlaced': Line interlaced.
        * 'checkerboard': Checkerboard interlaced.
        * 'left': Left eye only.
        * 'right': Right eye only.
        * 'horizontal': Side-by-side.
    verbose : bool
        print information about the camera. Default is False.
    Examples
    ---------
    >>> from fury import window, actor
    >>> scene = window.Scene()
    >>> a = actor.axes()
    >>> scene.add(a)
    >>> # uncomment below to record
    >>> # window.record(scene)
    >>> # check for new images in current directory
    """

    renWin.SetBorders(screen_clip)
    renWin.AddRenderer(scene)
    renWin.SetSize(size[0], size[1])

    if reset_camera:
        scene.ResetCamera()

    if stereo.lower() != 'off':
        enable_stereo(renWin, stereo)

    renderLarge = RenderLargeImage()
    renderLarge.SetInput(scene)
    renderLarge.SetMagnification(magnification)
    renderLarge.Update()

    ang = 0

    if cam_pos is not None:
        cx, cy, cz = cam_pos
        scene.GetActiveCamera().SetPosition(cx, cy, cz)
    if cam_focal is not None:
        fx, fy, fz = cam_focal
        scene.GetActiveCamera().SetFocalPoint(fx, fy, fz)
    if cam_view is not None:
        ux, uy, uz = cam_view
        scene.GetActiveCamera().SetViewUp(ux, uy, uz)

    cam = scene.GetActiveCamera()
    if verbose:
        print('Camera Position (%.2f, %.2f, %.2f)' % cam.GetPosition())
        print('Camera Focal Point (%.2f, %.2f, %.2f)' % cam.GetFocalPoint())
        print('Camera View Up (%.2f, %.2f, %.2f)' % cam.GetViewUp())

    for i in range(n_frames):
        scene.GetActiveCamera().Azimuth(ang)
        renderLarge = RenderLargeImage()
        renderLarge.SetInput(scene)
        renderLarge.SetMagnification(magnification)
        renderLarge.Update()

        if path_numbering:
            if out_path is None:
                filename = str(i).zfill(6) + '.png'
            else:
                filename = out_path + str(i).zfill(6) + '.png'
        else:
            if out_path is None:
                filename = 'fury.png'
            else:
                filename = out_path

        arr = numpy_support.vtk_to_numpy(renderLarge.GetOutput().GetPointData()
                                         .GetScalars())
        w, h, _ = renderLarge.GetOutput().GetDimensions()
        components = renderLarge.GetOutput().GetNumberOfScalarComponents()
        arr = arr.reshape((h, w, components))
        save_image(arr, filename)

        ang = +az_ang

    renWin.RemoveRenderer(scene)
