{{from gluon.serializers import json}}
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


    var d32py =  {
        vieweventmap: true,
        editable: {{=eventowner}},
        eventid: {{=str(eventrow.id)}},
        projid: {{=str(projid)}},
        edges: [],
        qtext: '',
        ajaxquesturl: "{{=URL('network','ajaxquest')}}",
        redraw: false
  };

    //TODO make js variables a single web2py object
        var ajaxquesturl = "{{=URL('network','ajaxquest')}}";

        var vieweventmap = true;
        var eventowner = {{=eventowner}};
        var eventid = {{=str(eventrow.id)}};
        var projid = {{=str(projid)}};


        var nodes = {{=XML(json(nodes))}};
        var links = {{=XML(json(links))}};
        var edges = [];
        var xpos = 0;
        var ypos = 0;
        var formaction=''
        var globalnode;

        //this move to graphd3v4 - however possibly not if want different sizes for different graphs
        //var height = 350 + (d3nodes.length * 25);
        //this will stay as may need to set from python
        var redraw = true;
        var itemUrl = '{{=URL('submit', 'new_questload.load')}}';

        console.log('nodes', nodes);
        //console.log('links', links);

        $('#itemload').hide();

        function initform(posx, posy) {
                $('#question_qtype').focus();
                $('#question_xpos').val(posx);
                $('#question_ypos').val(posy);
                $('#question_xpos__row').hide();
                $('#question_ypos__row').hide();
            };

        function questadd(action, posx, posy, node) {
            // so this will now unhide the div and populate the x and y coords of a new question or most other stuff
            // if editing - will be same - so we will call with an action and the fields from the inital form and it
            // should work fine we just need to set or remove the id somehow before submission and it should work ok
            // can add as hidden form element if required
            // function for editing with the form being filled in and the serverid is used to populate the recordid which
            // we just add if it is an edit and we are updating
            //ajax('{{=URL('submit','new_questload')}}'+'/'+0+'/'+eventid +'/' + projid + '/' + posx+'/'+posy+'/', ['bla'], 'itemload');
            $('#itemload').show();

            if ($('#notloggedin').is(':contains(logged)')) {
                out('You must be signed in in to add items')
            }

            xpos = posx;
            ypos = posy;
            formaction = action;
            globalnode = node;
            var serverid = '';
            


            if (action == 'New') {
                $.web2py.component(itemUrl + '/', 'itemload');
                setTimeout(function () {
                    initform(posx, posy)
                }, 1000);
            }

            if (action == 'Edit') {

                if (node.serverid == true) {
                serverid = node.serverid
                }
                else  {
                    serverid = node.title
                }
                console.log(serverid);

                $.web2py.component(itemUrl + '/' + serverid, 'itemload');
                //let's wait for fire event to do this properly in later version of web2py
                setTimeout(function () {
                    initform(posx, posy)
                }, 1000);

            }
        };


        function amendnode(qtext) {
              updatenode(globalnode, qtext);
        };

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


