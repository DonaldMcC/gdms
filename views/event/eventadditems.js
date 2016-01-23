
function showcountryValue(newValue)
{
	document.getElementById("viewscope_country").value=newValue;
    $('#subdivopt').empty();
    ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
    document.getElementById("viewscope_subdivision").value="Unspecified";
}

function showsubdivValue(newValue)
{
	document.getElementById("viewscope_subdivision").value=newValue;
}

function loadissues(itemsperpage)
{
	web2py_component('/gdms/default/actionload.load?items_per_page=1','issueload');
}

$(document).ready(function(){



     $('#viewscope_country__row .w2p_fc').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="{{=form.vars.country}}">{{=form.vars.country}}</option>   </select>');
   $('#viewscope_subdivision__row .w2p_fc').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="{{=form.vars.subdivision}}">{{=form.vars.subdivision}}</option> </select>');

    $('#viewscope_continent__row').hide();
    $('#viewscope_country__row .w2p_fw').hide();
    $('#viewscope_subdivision__row .w2p_fw').hide();



    if($("[id='scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide()
            $('#viewscope_country__row').hide()
            $('#viewscope_subdivision__row').hide()};
    if($("[id='scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').hide()
            $('#viewscope_subdivision__row').hide()};
    if($("[id='scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').hide()};
     if($("[id='scope4 Local']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').show();
            $('#viewscope_subdivision__row .w2p_fw').hide()};


    if ($('#filtersScope').prop('checked')==false){
       $('#viewscope_scope__row').hide();
       $('#viewscope_continent__row').hide();
       $('#viewscope_country__row').hide();
       $('#viewscope_subdivision__row').hide();}

    if ($('#filtersCategory').prop('checked')==false){
       $('#viewscope_category__row').hide();
        }

    if ($('#filtersAnswerGroup').prop('checked')==false){
       $('#viewscope_answer_group__row').hide();}


   $('#viewscope_showcat').change(function(){
           $('#TabAnswers').DataTable();
              $('#viewscope_category__row').toggle()});

    $('#filtersCategory').change(function(){
              $('#viewscope_category__row').toggle()
         $('#TabAnswers').DataTable();

         $('#TabIssues').DataTable();
           $('#TabActions').DataTable();

    });


        $('#filtersAnswerGroup').change(function(){
              $('#viewscope_answer_group__row').toggle()});



   $('#filtersScope').change(function(){
            if($('#filtersScope').prop('checked')==false) {
                $('#viewscope_scope__row').hide();
                $('#viewscope_continent__row').hide();
                $('#viewscope_country__row').hide();
                $('#viewscope_subdivision__row').hide();}
            else
                {$('#viewscope_scope__row').show();
            if($("[id='scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').show()
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide()
            $('#viewscope_country__row').hide()
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').hide()
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope4 Local']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').show()
            $('#viewscope_subdivision__row').show()};}

            });


   $('input[name=scope]').change(function(){
            if($("[id='scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide()
            $('#viewscope_country__row').hide()
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').hide()
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').show()
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').hide()};
            if($("[id='scope4 Local']").prop('checked'))
            {$('#viewscope_continent__row').show()
            $('#viewscope_country__row').show()
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').show()
            $('#viewscope_subdivision__row .w2p_fw').hide()};
            });

            $('#viewscope_continent ').change(function(){
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');});

            $('#viewscope_country').change(function(){
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');});



});