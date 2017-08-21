function showcountryValue(newValue)
{
	document.getElementById("question_country").value=newValue;
    $('#subdivopt').empty();
    ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
    document.getElementById("question_subdivision").value="Unspecified";
}

function showsubdivValue(newValue)
{
	document.getElementById("question_subdivision").value=newValue;
}

$(document).ready(function(){
   $(" body").tooltip({selector: '[data-toggle = popover]'});
   $('#question_continent__row').hide();
   $('#question_country__row').hide();
   $('#question_duedate__row').hide();
   $('#question_subdivision__row').hide();
   $('#question_coord__row').hide();
   $('#question_country__row .help-block').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="Unspecified">Unspecified</option>   </select>');
   $('#question_subdivision__row .help-block').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="Unspecified">Unspecified</option> </select>');
   if($('#question_resolvemethod option:selected').text()=='Resolved')
   {            $('#question_duedate__row').hide();
                $('#question_answer_group__row').hide();
   };


     $('#question_notes__label').append('<p></p><input type="BUTTON" id="wolflookup" ' +
         'value="Lookup Answer on Wolfram Alpha" class="btn btn-primary btn-xs btn-group-xs" onclick="wolfram_alpha_lookup()"></p>');

    $('#question_activescope').change(function(){
            if($('#question_activescope option:selected').text()=='2 Continental')
            {$('#question_continent__row').show();
            $('#question_country__row').hide();
            $('#question_subdivision__row').hide()};
            $('#question_coord__row').hide();
            if($('#question_activescope option:selected').text()=='1 Global')
            {$('#question_continent__row').hide();
            $('#question_country__row').hide();
            $('#question_subdivision__row').hide()};
            $('#question_coord__row').hide();
            if($('#question_activescope option:selected').text()=='3 National')
            {$('#question_continent__row').show();
            $('#question_country__row').show();
            $('#question_country').hide();
            $('#question_subdivision__row').hide()};
            $('#question_coord__row').hide();
            if($('#question_activescope option:selected').text()=='4 Provincial')
            {$('#question_continent__row').show();
            $('#question_country__row').show();
            $('#question_subdivision__row').show();
            $('#question_country').hide();
            $('#question_subdivision').hide();
            $('#question_coord__row').hide();};
            
            if($('#question_activescope option:selected').text()=='5 Local')
                {$('#question_continent__row').hide();
                $('#question_country__row').hide();
                $('#question_subdivision__row').hide();
                $('#question_coord__row').show();
                if ($(lwlat).val() == 0 && $(lwlng).val() == 0 && navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(success);
                };
            };})
            
            });
            
            $('#question_continent').change(function(){
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');});

            $('#question_country').change(function(){
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');});

            $('#question_resolvemethod').change(function(){
            $('#question_answer_group__row').show();
            $('#question_duedate__row').show();
            });
          $('#question_qtype').change(function(){
              if($('#question_qtype option:selected').text()=='issue')
                {$('#question_answers__row').hide()}
              if($('#question_qtype option:selected').text()=='action')
                {$('#question_answers__row').hide()}
              if($('#question_qtype option:selected').text()=='quest')
                {$('#question_answers__row').show()}
                });



function wolfram_alpha_lookup() {
    console.log('you called')
}


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

