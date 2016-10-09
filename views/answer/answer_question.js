function showurgValue(newValue)
{
	document.getElementById("userquestion_urgency").value=newValue;
}

function showimpValue()
{

    $('#userquestion_importance__row .w2p_fc').prepend(document.getElementById("userquestion_importance").value);

}


function showansValue(newValue)

{
	document.getElementById("userquestion_answer").value=newValue;
//document.getElementById("userquestion_urgency").innerHTML=newValue;

}

function showcountryValue(newValue)
{
	document.getElementById("userquestion_country").value=newValue;
    $('#subdivopt').empty();
    ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
    document.getElementById("userquestion_subdivision").value="Unspecified";
}

function showsubdivValue(newValue)
{
	document.getElementById("userquestion_subdivision").value=newValue;
}

$(document).ready(function() {

    $('#userquestion_importance').change(function () {
    $('#userquestion_importance__row .w2p_fc').html(document.getElementById("userquestion_importance").value + "/10");
    });

    $('#userquestion_urgency').change(function () {
    $('#userquestion_urgency__row .w2p_fc').html(document.getElementById("userquestion_urgency").value + "/10");
    });

    document.getElementById("userquestion_urgency").value=5;
    document.getElementById("userquestion_importance").value=5;

    $('#userquestion_country__row .w2p_fc').html('<select id="countryopt" name="countryopt" onchange="showcountryValue(this.value)"> <option value="Unspecified">Unspecified</option>   </select>');

    $('#userquestion_subdivision__row .w2p_fc').html('<select id="subdivopt" name="subdivopt" onchange="showsubdivValue(this.value)"> <option value="Unspecified">Unspecified</option> </select>');

    $('#userquestion_answer__row').hide();
    $('#userquestion_category__row').hide();
    $('#userquestion_activescope__row').hide();
    $('#userquestion_continent__row').hide();
    $('#userquestion_country__row').hide();
    $('#userquestion_subdivision__row').hide();
    $('#userquestion_coord__row').hide();

    $('#userquestion_changecat').change(function () {
        $('#userquestion_category__row').toggle();
    });
    $('#userquestion_changescope').change(function () {
        $('#userquestion_activescope__row').toggle();
        if ($('#userquestion_activescope :selected').text() == '2 Continental') {
            $('#userquestion_continent__row').show();
            $('#userquestion_country__row').hide();
            $('#userquestion_subdivision__row').hide();
            $('#userquestion_coord__row').hide();
        }

        if ($('#userquestion_activescope :selected').text() == '1 Global') {
            $('#userquestion_continent__row').hide();
            $('#userquestion_country__row').hide();
            $('#userquestion_subdivision__row').hide();
            $('#userquestion_coord__row').hide();
        }

        if ($('#userquestion_activescope :selected').text() == '3 National') {
            $('#userquestion_continent__row').show();
            $('#userquestion_country__row').show();
            $('#userquestion_country__row .w2p_fw').hide();
            $('#userquestion_subdivision__row').hide();
            $('#userquestion_coord__row').hide();
        }

        $('#countryopt').empty();
        ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');

        if ($('#userquestion_activescope :selected').text() == '4 Provincial') {
            $('#userquestion_continent__row').show();
            $('#userquestion_country__row').show();
            $('#userquestion_subdivision__row').show();
            $('#userquestion_coord__row').hide();
            $('#userquestion_country__row .w2p_fw').hide();
            $('#userquestion_subdivision__row .w2p_fw').hide();
            $('#subdivopt').empty();
            ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
        }

        if ($('#userquestion_activescope :selected').text() == '5 Local') {
            $('#userquestion_continent__row').hide();
            $('#userquestion_country__row').hide();
            $('#userquestion_subdivision__row').hide();
            $('#userquestion_coord__row').show();
        }
    });

    $('#userquestion_activescope').change(function () {
        if ($('#userquestion_activescope :selected').text() == '2 Continental') {
            $('#userquestion_continent__row').show();
            $('#userquestion_country__row').hide();
            $('#userquestion_subdivision__row').hide();
                $('#userquestion_coord__row').hide();
        }

        if ($('#userquestion_activescope :selected').text() == '1 Global') {
            $('#userquestion_continent__row').hide();
            $('#userquestion_country__row').hide();
            $('#userquestion_subdivision__row').hide();
                $('#userquestion_coord__row').hide();
        }

        if ($('#userquestion_activescope :selected').text() == '3 National') {
            $('#userquestion_continent__row').show();
            $('#userquestion_country__row').show();
                $('#userquestion_coord__row').hide();
            $('#userquestion_country__row .w2p_fw').hide();
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');
            $('#userquestion_subdivision__row').hide()
        }

        if ($('#userquestion_activescope :selected').text() == '4 Provincial') {
            $('#userquestion_continent__row').show();
            $('#userquestion_country__row').show();
                $('#userquestion_coord__row').hide();
            $('#userquestion_subdivision__row').show();
            $('#userquestion_country__row .w2p_fw').hide();
            $('#userquestion_subdivision__row .w2p_fw').hide();
        }

        if ($('#userquestion_activescope :selected').text() == '5 Local') {
            $('#userquestion_continent__row').hide();
            $('#userquestion_country__row').hide();
            $('#userquestion_subdivision__row').hide();
            $('#userquestion_coord__row').show();
        }

    });

    $('#userquestion_country').change(function () {
        $('#subdivopt').empty();
        ajax('{{=URL('submit','subdivn')}}', ['country'], 'subdivopt');
    });

    $('#userquestion_continent').change(function () {
        if ($('#userquestion_activescope :selected').text() != '2 Continental') {
            $('#userquestion_country__row .w2p_fw').hide();
            $('#countryopt').empty();
            ajax('{{=URL('submit','country')}}', ['continent'], 'countryopt');
        }
    });

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