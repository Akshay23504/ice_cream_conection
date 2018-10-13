$("#google_login").click(function () {
    if ($("#choose_role").val() == "") {
        $("#choose_role_error").show();
    } else if (!$("#terms_flag").is(":checked")) {
        $("#terms_flag_error").show();
    } else {
        $("#choose_role_error").hide();
        $("#terms_flag_error").hide();
        return true;
    }
    return false;
});

