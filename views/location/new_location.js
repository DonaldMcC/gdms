function showcountryValue(newValue)
{
	document.getElementById("locn_country").value=newValue;
    jQuery('#subdivopt').empty();
    ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
    document.getElementById("locn_subdivision").value="Unspecified";
}

function showsubdivValue(newValue)
{
	document.getElementById("locn_subdivision").value=newValue;
}



jQuery(document).ready(function(){

   $(" body").tooltip({selector: '[data-toggle = popover]'});
   $('#locn_country__row .help-block').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="Unspecified">Unspecified</option>   </select>');
   $('#locn_subdivision__row .help-block').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="Unspecified">Unspecified</option> </select>');

            $('#locn_country').hide();
            $('#locn_subdivision').hide();

            $('#locn_continent').change(function(){
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');});

            $('#locn_country').change(function(){
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');});


});