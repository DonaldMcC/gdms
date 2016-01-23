function showcountryValue(newValue)
{
	document.getElementById("location_country").value=newValue;
    jQuery('#subdivopt').empty();
    ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
    document.getElementById("location_subdivision").value="Unspecified";
}

function showsubdivValue(newValue)
{
	document.getElementById("location_subdivision").value=newValue;
}


jQuery(document).ready(function(){

   $(" body").tooltip({selector: '[data-toggle = popover]'});
   $('#location_country__row .w2p_fc').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="Unspecified">Unspecified</option>   </select>');
   $('#location_subdivision__row .w2p_fc').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="Unspecified">Unspecified</option> </select>');

            $('#location_country__row .w2p_fw').hide();
            $('#location_subdivision__row .w2p_fw').hide();

            $('#location_continent').change(function(){
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');});

            $('#location_country').change(function(){
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');});


});