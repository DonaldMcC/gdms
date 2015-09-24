var w2psa;
(function ($) {
    w2psa = {
        prefs : {},

        init_buttons : function() {
            $("#w2psa-buttons").on("click",".w2psa-button",function() {
                $(this).data("provider") && w2psa.signin($(this))
            });
            $("#social_button_form").submit(w2psa.submit);
        },

        init_dropdown : function() {
            var persona_option = $('#persona-option');
            if (persona_option) {
                persona_option.show();
                var form = $("#social_dropdown_form");
                var submit = false;
                form.submit(function() {
                    if ($('#backend-select').val() == 'persona') {

                        if (submit == true) {
                            return true;
                        }

                        navigator.id.get(function (assertion) {
                            if (assertion) {
                                $('#assertion').attr('value', assertion);
                                submit = true;
                                form.submit();
                            }  else {
                                alert('Some error occurred. Please try again...');
                                submit = false;
                            }
                        });

                        return false;
                    }
                });
            }
        },

        dosubmit : false,
        submit : function() {
            if ($("#backend").val() == 'persona') {
                if (w2psa.dosubmit == true) {
                    return true;
                }
                navigator.id.get(function (assertion) {
                    if (assertion) {
                        $('#assertion').attr('value', assertion);
                        w2psa.dosubmit = true;
                        $("#social_button_form").submit();
                    }  else {
                        alert('Some error occurred. Please try again...');
                        w2psa.dosubmit = false;
                    }
                });

                return false;
            }
        },

        signin : function(a) {
            var provider = a.data("provider");
            var form = $("#social_button_form");

            var hidden = document.getElementById("backend");
            if (hidden != null) {
                hidden.value = provider;
            }

            $("#w2psa-" + a.name).css("cursor", "wait");
            form.submit();
        }
    };
})(jQuery);
