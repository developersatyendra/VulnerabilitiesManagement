$(document).ready(

    //////////////////////////////////////////////////
    // Set form to read-only
    //
    SetReadonlyChangePassword(true),

    //////////////////////////////////////////
    // Click Change button
    //
    $("#changePassword").click(function () {
        SetReadonlyChangePassword(false)
    }),

    //////////////////////////////////////////
    // Click Cancel button
    //
    $("#cancelPasswordBtn").click(function () {
        $(this).closest('form').find("input[type=password], textarea").val("");
        $('#id_old_password').parent().removeClass("has-error");
        $('#id_old_password').next("span").text('');
        $('#id_new_password1').parent().removeClass("has-error");
        $('#id_new_password1').next("span").text('');
        $('#id_new_password2').parent().removeClass("has-error");
        $('#id_new_password2').next("span").text('');
        $("#changePasswordBtn").attr('disabled', true);
        SetReadonlyChangePassword(true);
    }),

    //////////////////////////////////////////
    // POST change password
    //
    $("#changePasswordPostForm").submit(function(e){
        $.post("/accounts/api/changemypassword", $(this).serialize(), function(data){
            if(data.status != 0){
                $("#titleInfo").text("Error");
                $("#msgInfo").text("Error: "+data.message+'. ');
                for(var prop in data.detail){
                    if(prop === "old_password"){
                        $('#id_old_password').parent().addClass("has-error");
                        $('#id_old_password').next().text(data.detail.old_password[0]);
                    }
                    else if(prop === "new_password1"){
                        $('#id_new_password1').parent().addClass("has-error");
                        $('#id_new_password1').next("span").text(data.detail.new_password1[0]);
                    }
                    else if(prop === "new_password2"){
                        $('#id_new_password2').parent().addClass("has-error");
                        $('#id_new_password2').next("span").text(data.detail.new_password2[0]);
                    }
                }
            }
            else{
                $("#titleInfo").text("About");
                $("#msgInfo").text("Your password is updated.");
                $('#id_old_password').parent().removeClass("has-error");
                $('#id_old_password').next("span").text('');
                $('#id_new_password1').parent().removeClass("has-error");
                $('#id_new_password1').next("span").text('');
                $('#id_new_password2').parent().removeClass("has-error");
                $('#id_new_password2').next("span").text('');
                SetReadonlyChangePassword(true);
            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
        }),


    //////////////////////////////////////////
    // Form on change
    //

    // Main Form
    $("#id_old_password").on("input", function () {
        $("#changePasswordBtn").attr('disabled', false);
    }),
    $("#id_new_password1").on("input", function () {
        $("#changePasswordBtn").attr('disabled', false);
    }),
    $("#id_new_password2").on("input", function () {
        $("#changePasswordBtn").attr('disabled', false);
    }),
    $('#changePasswordPostForm').change(function () {
        $("#changePasswordBtn").attr('disabled', false);
    }),
);


//////////////////////////////////////////
// Disable input until edit button is clicked
//
function SetReadonlyChangePassword(Enable) {
    if(Enable){
        $('#id_old_password').attr("readonly","readonly");
        $('#id_new_password1').attr("readonly","readonly");
        $("#id_new_password2").attr("readonly","readonly");
        $("#changePasswordInfoBtn").addClass("hidden");
    }
    else{
        $('#id_old_password').removeAttr("readonly");
        $('#id_new_password1').removeAttr("readonly");
        $("#id_new_password2").removeAttr("readonly");
        $("#changePasswordInfoBtn").removeClass("hidden");
    }
}
