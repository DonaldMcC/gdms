{{from gluon.serializers import json}}
    var inputmode = 'V'
    var newitems = false

    $('#radioBtn a').on('click', function(){
    var sel = $(this).data('title');
    var tog = $(this).data('toggle');
    $('#'+tog).prop('value', sel);
    inputmode = sel

    $('a[data-toggle="'+tog+'"]').not('[data-title="'+sel+'"]').removeClass('active').addClass('notActive');
    $('a[data-toggle="'+tog+'"][data-title="'+sel+'"]').removeClass('notActive').addClass('active');
})
        var ajaxquesturl = "{{=URL('network','ajaxquest')}}";
        //var d3nodes = {{=XML(d3nodes)}};

        var vieweventmap = true;
        var eventowner = {{=eventowner}}
        var eventid = {{=str(eventrow.id)}}  /*    var eventid = {{=eventrow.id}} this was in .load */
        var windowheight =  window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;

        var x = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth;
        var y = window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;

        console.log ('width', x, 'height', y)

        /*start of graphv4 */
        var nodes = {{=XML(json(nodes))}};
        var links = {{=XML(json(links))}};
        var edges = [];

        //this move to graphd3v4 - however possibly not if want different sizes for different graphs
        var height = 350 + (d3nodes.length * 25);
        //this will stay as may need to set from python
        var redraw = true;

        console.log('nodes', nodes);
        console.log('links', links);

    /* end of graphv4 */

        function requestLink(sourceId,targetId)
        {
            ajax('{{=URL('network','linkrequest')}}'+'/'+sourceId+'/'+targetId+'/', ['bla'], 'target');
        };

        function deleteLink(sourceId,targetId)
        {
        ajax('{{=URL('network','linkrequest')}}'+'/'+sourceId+'/'+targetId+'/delete/', ['bla'], 'target');
        };

        function deleteNode(nodeid, eventid)
        {
        ajax('{{=URL('network','nodedelete')}}'+'/'+nodeid+'/'+eventid+'/delete/', ['bla'], 'target');
        };

        function moveElement(sourceId, sourceposx, sourceposy)
        {
        ajax('{{=URL('event','move')}}'+'/'+{{=eventrow.id}}+'/'+sourceId+'/'+sourceposx+'/'+sourceposy+'/', ['bla'], 'target');
        };

        function out(m) {
        $('#message').html(m);
        };
