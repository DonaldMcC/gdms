/* This provides some default variables which should I think be moved to objects at some point soon */

        //below is vieweventmapd3v4
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


	$(".pushme").click(function () {
    var $element = $(this);
    $element.val(function(i, text) {
        editmode = !editmode;
        console.log (editmode);
        return text == $element.data('default-text') ? $element.data('new-text')
                                                     : $element.data('default-text');
    });
	});

    var nodes = {{=XML(json(nodes))}};
    var links = {{=XML(json(links))}};

        var vieweventmap = false;
        var eventowner = false;
        var redraw = true;



/* these are ajax functions and quite convenient to define here as then we get url syntax processing

 */
        function requestLink(sourceId,targetId)
        {
        ajax('{{=URL('network','linkrequest')}}'+'/'+sourceId+'/'+targetId+'/', ['bla'], 'ajaxlink');
        };

        function deleteLink(sourceId,targetId)
        {
        ajax('{{=URL('network','linkrequest')}}'+'/'+sourceId+'/'+targetId+'/delete/', ['bla'], 'ajaxlink');
        };

        function moveElement(sourceId, sourceposx, sourceposy)
        {
        ajax('{{=URL('event','move')}}'+'/'+0+'/'+sourceId+'/'+sourceposx+'/'+sourceposy+'/', ['bla'], 'ajaxlink');
        };

        var ajaxquesturl = "{{=URL('network','ajaxquest')}}?"

        function amendnode(qtext) {
              updatenode(d32py.globalnode, qtext);
        };

        function deleteNode(nodeid, eventid)
        {
        ajax('{{=URL('network','nodedelete')}}'+'/'+nodeid+'/'+eventid+'/delete/', ['bla'], 'target');
        };





    var d32py =  {
        vieweventmap: true,
        editable: {{=eventowner}},
        eventid: {{=str(eventrow.id)}},
        projid: {{=str(projid)}},
        edges: [],
        qtext: '',
        ajaxquesturl: "{{=URL('network','ajaxquest')}}",
        redraw: false,
        xpos: 0,
        ypos: 0,
        formaction: '',
        globalnode: []
  };

        var nodes = {{=XML(json(nodes))}};
        var links = {{=XML(json(links))}};
        var edges = [];

        var itemUrl = '{{=URL('submit', 'new_questload.load')}}';

        $('#itemload').hide();

        function initform(posx, posy) {
                $('#question_qtype').focus();
                $('#question_xpos').val(posx);
                $('#question_ypos').val(posy);
                $('#question_xpos__row').hide();
                $('#question_ypos__row').hide();
            };

        function questadd(action, posx, posy, node) {
            $('#itemload').show();

            if ($('#notloggedin').is(':contains(logged)')) {
                out('You must be signed in in to add items')
            }

            d32py.xpos = posx;
            d32py.ypos = posy;
            d32py.formaction = action;
            d32py.globalnode = node;
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

                $.web2py.component(itemUrl + '/' + serverid, 'itemload');
                //let's wait for fire event to do this properly in later version of web2py
                setTimeout(function () {
                    initform(posx, posy)
                }, 1000);

            }
        };


