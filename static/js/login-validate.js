$("#google_login").click(function () {
    $("#invalid_role_error").hide();
    if ($("#choose_role").val() == "") {
        $("#choose_role_error").show();
    } else if (!$("#terms_flag").is(":checked")) {
        $("#terms_flag_error").show();
    } else {
        $("#choose_role_error").hide();
        $("#terms_flag_error").hide();
        Cookies.set('icc_role_selected', $("#choose_role").val());
        return true;
    }
    return false;
});

