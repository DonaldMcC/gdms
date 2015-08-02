# - Coding UTF8 -
#
# Networked Decision Making
# Development Sites (source code): http://github.com/DonaldMcC/gdms
#
# Demo Sites (Google App Engine)
#   http://dmcc.pythonanywhere.com/gdmsprod/
#   http://dmcc.pythonanywhere.com/gdmsdemo/
#
# License Code: MIT
# License Content: Creative Commons Attribution 3.0
#
# Also visit: www.web2py.com
# or Groups: http://groups.google.com/group/web2py
# For details on the web framework used for this development
#
# With thanks to Guido, Massimo and many other that make this sort of thing
# much easier than it used to be
#
# This file was sourced entirely from uforum code at
# https://github.com/corebyte/uforum
#
#########################################################################

def generate_thumbnail(image, nx=120, ny=120, static=False):
    """
    Makes thumbnail version of given image with given maximum width & height
    in uploads folder with filename based on original image name

    If static=True thumbnail will be placed in static/thumbnails
    so it can be used without the need of a download controller

    requires PIL
    """
    if not image:
        return
    try:
        import os
        from PIL import Image

        img = Image.open(os.path.join(request.folder, 'uploads', image))
        img.thumbnail((nx, ny), Image.ANTIALIAS)
        root, ext = os.path.splitext(image)
        thumb = '%s_thumb_%s_%s%s' % (root, nx, ny, ext)
        img.save(os.path.join(request.folder, 'uploads', thumb))
        if static:
            file_dir = os.path.join(request.folder, 'static', 'thumbnails')
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            img.save(os.path.join(file_dir, thumb))
            os.path.join(file_dir, thumb)
        return thumb
    except:
        return
