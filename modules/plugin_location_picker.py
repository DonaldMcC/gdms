# -*- coding: utf-8 -*-
"""
This plugin provides a widget and validator for geometry fields representing a point on the map.

    Usage:
    from plugin_location_picker import IS_GEOLOCATION, location_widget
    db.table.field.requires = IS_GEOLOCATION()
    db.table.field.widget = location_widget()
"""
__author__ = 'Leonel Câmara'
__email__ = 'leonel.camara@i-am.pt leonelcamara@gmail.com'
__copyright__ = 'Copyright(c) 2014 Leonel Câmara'
__license__ = 'BEER-WARE'
__version__ = '0.11'
__status__ = 'Development'  # possible options: Prototype, Development, Production


from gluon import *
from gluon.storage import Storage
from gluon.sqlhtml import FormWidget
from gluon.tools import json_parser
import copy


FILES = [
            URL('static', 'plugin_location_picker/jquery.geolocation.edit.js'),
        ]

def _set_files(files):
    """
    This function was actually taken from one of the freely available plugins in http://dev.s-cubism.com/

    It is under the MIT license.
    """
    if current.request.ajax:
        current.response.js = (current.response.js or '') + """;(function ($) {
var srcs = $('script').map(function(){return $(this).attr('src');}),
    hrefs = $('link').map(function(){return $(this).attr('href');});
$.each(%s, function() {
    if ((this.slice(-3) == '.js') && ($.inArray(this.toString(), srcs) == -1)) {
        var el = document.createElement('script'); el.type = 'text/javascript'; el.src = this;
        document.body.appendChild(el);
    } else if ((this.slice(-4) == '.css') && ($.inArray(this.toString(), hrefs) == -1)) {
        $('<link rel="stylesheet" type="text/css" href="' + this + '" />').prependTo('head');
        if (/* for IE */ document.createStyleSheet){document.createStyleSheet(this);}
}});})(jQuery);""" % ('[%s]' % ','.join(["'%s'" % f.lower().split('?')[0] for f in files]))
    else:
        current.response.files[:0] = [f for f in files if f not in current.response.files]

def location_widget(**settings):
    """
    Possible settings:
    width -- width of the map container default 360.
    height -- height of the map container default 280.
    mapid -- id of the map container default random.
    latid -- id of the latitude input default random.
    lngid -- id of the longitude input default random.
    address --
    map_options -- see https://developers.google.com/maps/documentation/javascript/reference?csw=1#MapOptions
    marker_options -- see https://developers.google.com/maps/documentation/javascript/reference?csw=1#MarkerOptions
                      
                      As an example, of map and marker_options, to set initial 
                      position you can use:
                      db.table.field.widget=location_widget(
                        map_options = {'center': {'lat': initial_lat, 'lng': initial_lng}}
                        marker_options = {'position': {'lat': initial_lat, 'lng': initial_lng}}
                      )
    """
    def randid():
        import random
        return 'lw-' + str(random.random())[2:]

    default_settings = Storage(
        width=360,
        height=280,
        mapid='lw_map',
        latid='lw_lat',
        lngid='lw_lng',
        map_options = {},
        marker_options = {}  
    )

    if settings is not None:
        default_settings.update(settings)
    
    settings = default_settings

    def widget(field, value, **attributes):
        _set_files(FILES)

        default = {'value': value}
        attributes = FormWidget._attributes(field, default, **attributes)

        if value:
            lat, lng = IS_GEOLOCATION.parse_geopoint(value)
            settings.marker_options['position'] = {'lat': lat, 'lng': lng}
            settings.map_options['center'] = {'lat': lat, 'lng': lng}
        else:
            if 'position' in settings.marker_options:
                lat, lng = (settings.marker_options['position']['lat'], settings.marker_options['position']['lng'])
            else:
                lat, lng = 0.0, 0.0


        html = CAT(
            DIV(
                DIV(INPUT(_id=settings.latid, _value=lat, _class='latitude form-control'), _class='col-lg-6 col-md-6'),
                DIV(INPUT(_id=settings.lngid, _value=lng, _class='longitude form-control'), _class='col-lg-6 col-md-6'),
                INPUT(_type='hidden', **attributes),
            _class='row form-group'),
            DIV(
                DIV(DIV(_id=settings.mapid, _class='map', _style='width: %(width)spx; height: %(height)spx' % settings), _class='col-lg-12 col-md-12'),
                _class='row form-group')
        )
        hidden_id = attributes['_id']
        
        javascript = SCRIPT("""
            $('#%(mapid)s').geolocate({
                lat: '#%(latid)s',
                lng: '#%(lngid)s',
                markerOptions: %(marker_options)s,
                mapOptions: %(map_options)s
                });
            $('#%(latid)s').closest('form').submit(function() {
                    $('#%(hidden_id)s').val('POINT (' + $('#%(latid)s').val() + ' ' + $('#%(lngid)s').val() + ')');
                });        
            """ % {
                    'mapid' : settings.mapid,
                    'latid' : settings.latid,
                    'lngid' : settings.lngid,
                    'marker_options' : json_parser.dumps(settings.marker_options),
                    'map_options' : json_parser.dumps(settings.map_options),
                    'hidden_id': hidden_id
                }
            )
        return CAT(html, javascript)

    return widget


from gluon.validators import Validator, translate
import re


class IS_GEOLOCATION(Validator):
    """ 
    Validate that the input is a location within latitude and longitude
    constraints.
    """
    regex_geopoint = re.compile(r"""POINT *\((?P<lat>-?[\d\.]+) (?P<lng>-?[\d\.]+)\)""")

    def __init__(self, minlat=-90, maxlat=90, 
                       minlng=-180, maxlng=180,
                error_message='Invalid coordinates'):
        self.minlat = minlat
        self.maxlat = maxlat
        self.minlng = minlng
        self.maxlng = maxlng
        self.error_message = error_message

    @staticmethod
    def parse_geopoint(value):
        """ Returns a tuple (lat, lng) from a POINT (lat lng) """
        match = IS_GEOLOCATION.regex_geopoint.search(value)
        return float(match.group('lat')), float(match.group('lng'))

    def __call__(self, value):
        try:
            lat, lng = self.parse_geopoint(value)
            if (self.minlat <= lat <= self.maxlat) and (self.minlng <= lng <= self.maxlng):
                return (value, None)
            else:
                return (value, translate(self.error_message))
        except:
            return (value, translate(self.error_message))

