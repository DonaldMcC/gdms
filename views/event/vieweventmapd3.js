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
        var d3nodes = {{=XML(d3nodes)}};
        //console.log (d3nodes);
        var vieweventmap = true;
        var eventowner = {{=eventowner}}
        var eventid = {{=str(eventrow.id)}}  /*    var eventid = {{=eventrow.id}} this was in .load */
        var windowheight =  window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;
        
        /*var height = 350 + (d3nodes.length * 60); */
        var height = 320 + (d3nodes.length * 50);
        
        /* would like to combine above two sensibly but maybe that is scaling reduce heigh to 300 for now and then test */
        
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

        function deleteNode(nodeid, eventid)
        {
            console.log('delete node')
        ajax('{{=URL('network','nodedelete')}}'+'/'+nodeid+'/'+eventid+'/delete/', ['bla'], 'target');
        };

        function moveElement(sourceId, sourceposx, sourceposy)
        {

        ajax('{{=URL('event','move')}}'+'/'+{{=eventrow.id}}+'/'+sourceId+'/'+sourceposx+'/'+sourceposy+'/', ['bla'], 'target');
        };


        function out(m) {
        $('#message').html(m);
        };