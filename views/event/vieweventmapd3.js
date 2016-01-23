    var editmode = false;
    var newitems = false;

	$(".pushme").click(function () {
    var $element = $(this);
    $element.val(function(i, text) {
        editmode = !editmode
        console.log (editmode)
        return text == $element.data('default-text') ? $element.data('new-text')
                                                     : $element.data('default-text');
    });
	});

        var ajaxquesturl = '{{=URL('network','ajaxquest')}}?'
        var d3nodes = {{=XML(d3nodes)}};
        var vieweventmap = true
        var eventowner = {{=eventowner}}
        var eventid = {{=str(eventrow.id)}}  /*    var eventid = {{=eventrow.id}} this was in .load */
        var height = 350 + (d3nodes.length * 60);
        var redraw = false;

        /*var d3edges = [{"source":2,"target":3}]
        var d3edges = [{"source":13,"target":14}]*/
        var d3edges = {{=XML(d3edges)}};

        d3edges.forEach(function(e, i){
              d3edges[i] = {source: d3nodes.filter(function(n){return n.serverid == e.source;})[0],
                          target: d3nodes.filter(function(n){return n.serverid == e.target;})[0]}});

        function requestLink(sourceId,targetId)
        {
            ajax('{{=URL('network','linkrequest')}}'+'/'+sourceId+'/'+targetId+'/', ['bla'], 'target');
        };

        function deleteLink(sourceId,targetId)
        {
        ajax('{{=URL('network','linkrequest')}}'+'/'+sourceId+'/'+targetId+'/delete/', ['bla'], 'target');
        };

        function moveElement(sourceId, sourceposx, sourceposy)
        {

        ajax('{{=URL('event','move')}}'+'/'+{{=eventrow.id}}+'/'+sourceId+'/'+sourceposx+'/'+sourceposy+'/', ['bla'], 'target');
        };

        $(" body").tooltip({selector: '[data-toggle = popover]'});

        function out(m) {
        $('#message').html(m);
        };