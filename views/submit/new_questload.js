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

var qtext ='';

$(document).ready(function(){
   $(" body").tooltip({selector: '[data-toggle = popover]'});
   $('#question_continent__row').hide();
   $('#question_country__row').hide();
   $('#question_duedate__row').hide();
   $('#question_subdivision__row').hide();
   $('#question_coord__row').hide();
   $('#question_country__row .help-block').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="Unspecified">Unspecified</option>   </select>');
   $('#question_subdivision__row .help-block').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="Unspecified">Unspecified</option> </select>');
    $('#question_activescope').change(function(){
            if($('#question_activescope option:selected').text()=='2 Continental')
            {$('#question_continent__row').show();
            $('#question_country__row').hide();
            $('#question_subdivision__row').hide()};
            $('#question_coord__row').hide();
            if($('#question_activescope option:selected').text()=='1 Global')
            {$('#question_continent __row').hide();
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
            $('#question_duedate__row').show();

            });
          $('#question_qtype').change(function(){
              if($('#question_qtype option:selected').text()=='issue')
                {$('#question_answers__row').hide()}
              if($('#question_qtype').find('option:selected').text()=='action')
                {$('#question_answers__row').hide()}
              if($('#question_qtype option:selected').text()=='quest')
                {$('#question_answers__row').show()}
                });

            $('#question_questiontext').blur(function () {
                console.log('you blurred');
                qtext = $('#question_questiontext').val();
            });

            $('#myform').submit(function () {
                $('#itemload').hide();
                console.log('I ran on submit' + d32py.formaction);
                if (d32py.formaction=='New') {
                        addnode(qtext, d32py.xpos, d32py.ypos);
                    }
                    else {
                        amendnode(qtext);
                    }

                $("html, body").animate({scrollTop: 0}, "slow")
            });
