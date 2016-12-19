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
        var qtext = '';

        //this move to graphd3v4 - however possibly not if want different sizes for different graphs
        //var height = 350 + (d3nodes.length * 25);
        //this will stay as may need to set from python
        var redraw = true;

        console.log('nodes', nodes);
        //console.log('links', links);

        $('#itemload').hide();

        function questadd(action, posx, posy, node)
        {
            // so this will now unhide the div and populate the x and y coords of a new question or most other stuff
            // if editing - will be same - so we will call with an action and the fields from the inital form and it
            // should work fine we just need to set or remove the id somehow before submission and it should work ok
            // can add as hidden form element if required
            // function for editing with the form being filled in and the serverid is used to populate the recordid which
            // we just add if it is an edit and we are updating
            //ajax('{{=URL('submit','new_questload')}}'+'/'+0+'/'+eventid +'/' + projid + '/' + posx+'/'+posy+'/', ['bla'], 'itemload');
            $('#itemload').show();
            if (action=='New') {
                $('#question_qtype').focus();
                $('#question_xpos').val(posx);
                $('#question_ypos').val(posy);
                //lets make sure ID of hidden element removed here
            };

            if (action=='Edit') {
                $('#question_qtype').val(node.qtype);
                $('#question_questiontext').val(node.title);
                $('#question_category').val(node.category);
                $('#question_activescope').val(node.activescope);
                $('#question_continent').val(node.continent);
                $('#question_country').val(node.country);
                $('#question_subdivision').val(node.subdivision);
                $('#question_answers').val(node.answers);
                $('#question_xpos').val(posx);
                $('#question_ypos').val(posy);
                //now add all the other standard fields including the hidden ones
                // will also need to populate the id of the field in the hidden section
                // and probably test to see if it is already there
                $('#question_questiontext').focus();
            };

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
