
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


$(document).ready(function(){
          $(" body").tooltip({selector: '[data-toggle = popover]'});

     $('#viewscope_country__row .w2p_fc').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="{{=form.vars.country}}">{{=form.vars.country}}</option>   </select>');
   $('#viewscope_subdivision__row .w2p_fc').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="{{=form.vars.subdivision}}">{{=form.vars.subdivision}}</option> </select>');

    $('#viewscope_continent__row').hide();
    $('#viewscope_country__row .w2p_fw').hide();
    $('#viewscope_subdivision__row .w2p_fw').hide();
    $('#viewscope_coord__row').hide();
    $('#viewscope_responsible__row').hide();
    $('#viewscope_searchrange__row').hide();


    $('input[type=checkbox]').each(function() {
        if ($(this).prop('checked')) {
    $(this).next().addClass('btn-success');
        }
        });
    
    $('input[type=checkbox]').click(function () {
        $(this).next().toggleClass("btn-success")
        });

    if($("[id='view_scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()
            $('#viewscope_coord__row').hide()
            $('#viewscope_searchrange__row').hide()};
    if($("[id='view_scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()};
    if($("[id='view_scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').hide()};
     if($("[id='view_scope4 Provincial']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').show();
            $('#viewscope_subdivision__row .w2p_fw').hide()};
     if($("[id='view_scope5 Local']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide();
            $('#viewscope_coord__row').show();
            $('#viewscope_searchrange__row').show();};


    if ($('#filtersScope').prop('checked')==false){
       $('#viewscope_view_scope__row').hide();
       $('#viewscope_continent__row').hide();
       $('#viewscope_country__row').hide();
       $('#viewscope_subdivision__row').hide();
       $('#viewscope_coord__row').hide();
       $('#viewscope_responsible__row').hide();
       $('#viewscope_searchrange__row').hide();}

    if ($('#filtersCategory').prop('checked')==false){
       $('#viewscope_category__row').hide();
        }

    if ($('#filtersEvent').prop('checked')==false){
       $('#viewscope_eventid__row').hide();
    }
    
    if ($('#filtersProject').prop('checked')==false){
       $('#viewscope_projid__row').hide();
    }
    
    if ($('#filtersAnswerGroup').prop('checked')==false){
       $('#viewscope_answer_group__row').hide();}

    if ($('#filtersresponsible').prop('checked')==false){
       $('#viewscope_responsible__row').hide();}
       
    if ($('#filtersDate').prop('checked')==false){
       $('#viewscope_startdate__row').hide();
       $('#viewscope_enddate__row').hide();}

   $('#viewscope_showcat').change(function(){
           $('#TabAnswers').DataTable();
              $('#viewscope_category__row').toggle()});

    $('#filtersCategory').change(function(){
              $('#viewscope_category__row').toggle();
         $('#TabAnswers').DataTable();

         $('#TabIssues').DataTable();
           $('#TabActions').DataTable();

    });

        $('#filtersDate').change(function(){
       $('#viewscope_startdate__row').toggle();
       $('#viewscope_enddate__row').toggle();
    });
    
        $('#filtersAnswerGroup').change(function(){
              $('#viewscope_answer_group__row').toggle()});

        $('#filtersEvent').change(function(){
              $('#viewscope_eventid__row').toggle()});
              
        $('#filtersProject').change(function(){
              $('#viewscope_projid__row').toggle()});

        $('#filtersResponsible').change(function(){
              $('#viewscope_responsible__row').toggle()});

   $('#filtersScope').change(function(){
            if($('#filtersScope').prop('checked')==false) {
                $('#viewscope_view_scope__row').hide();
                $('#viewscope_continent__row').hide();
                $('#viewscope_country__row').hide();
                $('#viewscope_subdivision__row').hide()
                $('#viewscope_coord__row').hide();
                $('#viewscope_responsible__row').hide();
                $('#viewscope_searchrange__row').hide();;}
            else
                {$('#viewscope_view_scope__row').show();
            if($("[id='scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_subdivision__row').hide()};
            $('#viewscope_coord__row').hide();
            $('#viewscope_searchrange__row').hide();
            if($("[id='scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()
            $('#viewscope_coord__row').hide();
            $('#viewscope_searchrange__row').hide();};
            if($("[id='scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()
            $('#viewscope_coord__row').hide();
            $('#viewscope_searchrange__row').hide();};
            if($("[id='scope4 Provincial']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_subdivision__row').show()
            $('#viewscope_coord__row').hide();
            $('#viewscope_searchrange__row').hide()}
            if($("[id='scope5 Local']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()
            $('#viewscope_coord__row').show()
            $('#viewscope_searchrange__row').show()}
            
            ;}

            });


   $('input[name=view_scope]').change(function(){
            //console.log('scope change')
            if($("[id='view_scope1 Global']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()
            $('#viewscope_coord__row').hide()
            $('#viewscope_searchrange__row').hide()};
            if($("[id='view_scope2 Continental']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide()
            $('#viewscope_coord__row').hide()
            $('#viewscope_searchrange__row').hide()};
            if($("[id='view_scope3 National']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').hide()
            $('#viewscope_coord__row').hide()
            $('#viewscope_searchrange__row').hide()};
            if($("[id='view_scope4 Provincial']").prop('checked'))
            {$('#viewscope_continent__row').show();
            $('#viewscope_country__row').show();
            $('#viewscope_country__row .w2p_fw').hide();
            $('#viewscope_subdivision__row').show();
            $('#viewscope_subdivision__row .w2p_fw').hide()
            $('#viewscope_coord__row').hide()
            $('#viewscope_searchrange__row').hide()};
            if($("[id='view_scope5 Local']").prop('checked'))
            {$('#viewscope_continent__row').hide();
            $('#viewscope_country__row').hide();
            $('#viewscope_subdivision__row').hide();
            $('#viewscope_coord__row').show()
            $('#viewscope_searchrange__row').show()
            if ($(lwlat).val() == 0 && $(lwlng).val() == 0 && navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(success);
                };
            }
            });

            $('#viewscope_continent ').change(function(){
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');});

            $('#viewscope_country').change(function(){
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');});



});

 var lwlat = "#lw_lat";
 var lwlng = "#lw_lng";

//only update with current location if not set on the record already and for 
//here we will round to two decimal places of current location for issue reporting   

function geo_refresh() {
$("#lw_map").geolocate({
	lat: lwlat,
	lng: lwlng
});
    }

function success(position) {
     $(lwlat).val(position.coords.latitude.toFixed(2));
     $(lwlng).val(position.coords.longitude.toFixed(2));
     geo_refresh();
    };
   
$(lwlat ).change(function() {
     geo_refresh();
});   

$(lwlat ).change(function() {
     geo_refresh();
}); 