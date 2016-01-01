function showansValue(newValue)
{
	document.getElementById("eventmap_correctans").value=newValue;
}

$(document).ready(function() {

    $("input[name=ans][value='{{=correctans}}']").prop("checked",true);

    $('#eventmap_correctans__row').hide();
    $('#eventmap_adminresolve__row').hide();
    $('#eventmap_queststatus__row').hide();

    $('input[name=ans]').change(function () {
       /* $('#eventmap_adminresolve__row').toggle();*/
        $("input[name=adminresolve]").prop("checked",true);
    });

});