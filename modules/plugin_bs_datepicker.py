# -*- coding: utf-8 -*-
"""
Integrates bootstrap-datepicker nicely into web2py.
"""

__author__ = 'Leonel Câmara'
__email__ = 'leonel.camara@i-am.pt leonelcamara@gmail.com'
__copyright__ = 'Copyright(c) 2014 Leonel Câmara'
__license__ = 'BEER-WARE'
__version__ = '0.11'
__status__ = 'Development'  # possible options: Prototype, Development, Production


from gluon import *
from gluon.sqlhtml import FormWidget



def bsdatepicker_widget(**settings):
    """
    Usage:
    
    from plugin_bs_datepicker import bsdatepicker_widget
    db.table.field.widget = bsdatepicker_widget()

    Another example:

    db.table.field.widget = bsdatepicker_widget(startView=2)

    Possible settings:
    weekStart -- defaults to 0, day of the week start. 0 for Sunday - 6 for Saturday
    startView  -- defaults to  0 = 'days'  set the start view mode. Accepts: 'days', 'months', 'years', 0 for days, 1 for months and 2 for years.
    minViewMode -- defaults to 0 = 'days'  set a limit for view mode. Accepts: 'days', 'months', 'years', 0 for days, 1 for months and 2 for years.
    """

    def widget(field, value, **attributes):
        default = {'value': value}
        
        attributes = FormWidget._attributes(field, default, **attributes)
        attributes['_class'] = 'form-control datepicker'
                    
        dateinput = INPUT(**attributes)
        settings_str = ',\n'.join(item[0] + ':' + str(item[1]) for item in settings.iteritems()) if settings else ''
        javascript = SCRIPT("""
            $('head').append($('<link  href="%(cssurl)s" type="text/css" rel="stylesheet" />'));
            $.getScript('%(scripturl)s').done(function(){
                $('#%(_id)s').datepicker({
                    format: w2p_ajax_date_format.replace('%%Y', 'yyyy').replace('%%m', 'mm').replace('%%d', 'dd'),
                    %(settings)s
                })
            });
            """ % {
                'cssurl': URL('static', 'plugin_bs_datepicker/datepicker.css'),
                'scripturl': URL('static', 'plugin_bs_datepicker/bootstrap-datepicker.js'),
                '_id': dateinput.attributes['_id'],
                'settings': settings_str
            })
        return CAT(dateinput, javascript)

    return widget

    
def bsdatetimepicker_widget(**settings):
    """
    Usage:
    
    from plugin_bs_datepicker import bsdatepicker_widget
    db.table.field.widget = bsdatepicker_widget()

    Another example:

    db.table.field.widget = bsdatepicker_widget(startView=2)

    Possible settings:
    weekStart -- defaults to 0, day of the week start. 0 for Sunday - 6 for Saturday
    startView  -- defaults to  0 = 'days'  set the start view mode. Accepts: 'days', 'months', 'years', 0 for days, 1 for months and 2 for years.
    minViewMode -- defaults to 0 = 'days'  set a limit for view mode. Accepts: 'days', 'months', 'years', 0 for days, 1 for months and 2 for years.
    """

    def widget(field, value, **attributes):
        default = {'value': value}
        
        attributes = FormWidget._attributes(field, default, **attributes)
        attributes['_class'] = 'form-control datepicker'
                    
        dateinput = INPUT(**attributes)
        settings_str = ',\n'.join(item[0] + ':' + str(item[1]) for item in settings.iteritems()) if settings else ''
        javascript = SCRIPT("""
            $('head').append($('<link  href="%(cssurl)s" type="text/css" rel="stylesheet" />'));
            $.getScript('%(scripturl)s').done(function(){
                $('#%(_id)s').datetimepicker({
                    format: w2p_ajax_date_format.replace('%%Y', 'yyyy').replace('%%m', 'mm').replace('%%d', 'dd'),
                    %(settings)s
                })
            });
            """ % {
                'cssurl': URL('static', 'plugin_bs_datepicker/datetimepicker.css'),
                'scripturl': URL('static', 'plugin_bs_datepicker/bootstrap-datetimepicker.js'),
                '_id': dateinput.attributes['_id'],
                'settings': settings_str
            })
        return CAT(dateinput, javascript)

    return widget