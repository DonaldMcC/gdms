{{from gluon.serializers import json}}
//TO DO will make a single global object for the variables and options here
    var inputmode = 'V';
    var newitems = false;

    $('#radioBtn a').on('click', function(){
    var sel = $(this).data('title');
    var tog = $(this).data('toggle');
    $('#'+tog).prop('value', sel);
    inputmode = sel

    $('a[data-toggle="'+tog+'"]').not('[data-title="'+sel+'"]').removeClass('active').addClass('notActive');
    $('a[data-toggle="'+tog+'"][data-title="'+sel+'"]').removeClass('notActive').addClass('active');
});
        var ajaxquesturl = "{{=URL('network','ajaxquest')}}";

        var vieweventmap = true;
        var eventowner = {{=eventowner}};
        var eventid = {{=str(eventrow.id)}};
        var projid = {{=str(projid)}};
        /*    var eventid = {{=eventrow.id}} this was in .load */
        //var windowheight =  window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;

        //var x = window.innerWidth || docEl.clientWidth || bodyEl.clientWidth;
        //var y = window.innerHeight|| docEl.clientHeight|| bodyEl.clientHeight;

        //console.log ('width', x, 'height', y)

        /*start of graphv4 */
        var nodes = {{=XML(json(nodes))}};
        var links = {{=XML(json(links))}};
        var edges = [];
        var qtext = '';

        //this move to graphd3v4 - however possibly not if want different sizes for different graphs
        //var height = 350 + (d3nodes.length * 25);
        //this will stay as may need to set from python
        var redraw = true;

        console.log('nodes', nodes);
        //console.log('links', links);


        function questadd(posx, posy)
        {

            // so this will now unhide the div and populate the x and y coords of a new question - will be separate
            // function for editing with just the text being editable for draft items
            //ajax('{{=URL('submit','new_questload')}}'+'/'+0+'/'+eventid +'/' + projid + '/' + posx+'/'+posy+'/', ['bla'], 'itemload');
            $('#itemload').show();
            $('#question_xpos').val(posx);
            $('#question_ypos').val(posy);
            $('#question_qtype').focus();
            $('#question_questiontext').blur(function() {
                    qtext = $('#question_questiontext').val();
                    });
            $('#myform').submit(function() {
                    $('#itemload').hide();
                    addnode(qtext, posx, posy);
                     $("html, body").animate({ scrollTop: 0 }, "slow");
                    });
        }


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
