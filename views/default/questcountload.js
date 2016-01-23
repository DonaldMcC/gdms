    $(document).ready(function() {
        $("#GroupTot").click(function() {
      grouptoggle();
  });
          $("#CatTot").click(function() {
      cattoggle();
  });
});


    function grouptoggle() {
        $(".grouprow").toggleClass("in");
        $("#GroupTotSpan").toggleClass("glyphicon glyphicon-plus").toggleClass("glyphicon glyphicon-minus");
    }

function cattoggle() {
        $(".catrow").toggleClass("in");
        $("#CatTotSpan").toggleClass("glyphicon glyphicon-plus").toggleClass("glyphicon glyphicon-minus");
    }