
//////////////////////////////////////////////////
var geturl = '/accounts/api/getmyaccount';

//////////////////////////////////////////////////
var flagDataStored = false;
var dataStored;
$(document).ready(

    //////////////////////////////////////////////////
    // Fill data to forms and set them to readonly state
    //
    $.when(FillInfo()).done(function (result) {
        dataStored = result;
        flagDataStored = true;
    }),
    SetReadonly(true),

    //////////////////////////////////////////
    // Click Edit button
    //
    $("#edit").click(function () {
        SetReadonly(false)
    }),

    //////////////////////////////////////////
    // Click Delete button
    //
    $("#delete").click(function () {
        flagDeleteOption = 0;
        $('#msgOnDelete').text("Are you sure to delete this project?");
        $("#warningOnDeleteModal").modal("show");
    }),

    //////////////////////////////////////////
    // Click Delete button from warning modal
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');
        var data = [];

        // Create ID array
        var ids = new Array();
        ids.push($("#id_id").val());
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('/projects/api/deleteproject', $.param(data),
             function(data){
                if(data.status == 0){
                    $('#warningOnDeleteModal').modal('hide');
                    $("#titleInfo").text("About");
                    $("#msgInfo").text("The project is deleted.");
                    $("#infoModal").modal("show");
                    $("#infoModal").on('hidden.bs.modal', function (e) {
                          $( location ).attr("href", '/projects');
                    });
                }
                else{
                    $('#warningOnDeleteModal').modal('hide');
                    $("#titleInfo").text("Error");
                    $("#msgInfo").text("Error: "+data.message+'. '+ data.message);
                    $("#infoModal").modal("show");
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //////////////////////////////////////////
    // Click Cancel button
    //
    $("#cancelUpdateBtn").click(function () {
        if(flagDataStored){
            FillInfo(dataStored);
        }
        else{
            FillInfo();
        }
        SetReadonly(true);
    }),

    //////////////////////////////////////////
    // POST update
    //
    $("#editMyAccountPostForm").submit(function(e){
        $.post("/accounts/api/updatemyaccount", $(this).serialize(), function(data){
            if(data.status != 0){
                $("#titleInfo").text("Error");
                $("#msgInfo").text("Error: "+data.message+'. '+ data.detail.name[0]);
            }
            else{
                $("#titleInfo").text("About");
                $("#msgInfo").text("Your account information is updated.");
                SetReadonly(true);
            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
        }),


    //////////////////////////////////////////
    // Form editMyAccountPostForm on change
    //

    // Main Form
    $("#id_first_name").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_last_name").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_email").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $('#editMyAccountPostForm').change(function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
);

//////////////////////////////////////////
// Fill in information of project
//
function FillInfo(input) {
    flagDataStored = false;
    var deferred = new $.Deferred();
    if(input === undefined) {
        $.ajax({
            type: "GET",
            url: geturl,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                //  Fill in form
                $('#id_username').val(data.object.username);
                $('#id_date_joined').val(FormattedDate(data.object.date_joined));
                $('#id_first_name').val(data.object.first_name);
                $("#id_last_name").val(data.object.last_name);
                $("#id_email").val(data.object.email);
                deferred.resolve(data);
            }
        });
    }
    else {
        // Fill breadcrumb
        $('#brScan').text(input.object.name);

        //  Fill in form
        $('#id_username').val(input.object.username);
        $('#id_date_joined').val(FormattedDate(input.object.date_joined));
        $('#id_first_name').val(input.object.first_name);
        $("#id_last_name").val(input.object.last_name);
        $("#id_email").val(input.object.email);
        deferred.resolve(input);
    }
    return deferred.promise();
}


//////////////////////////////////////////
// Disable input until edit button is clicked
//
function SetReadonly(Enable) {
    if(Enable){
        $("#saveInfoBtn").attr('disabled', true);

        $('#id_first_name').attr("readonly","readonly");
        $('#id_last_name').attr("readonly","readonly");
        $("#id_email").attr("readonly","readonly");
        $("#myAccountInfoBtn").addClass("hidden");
    }
    else{
        $('#id_first_name').removeAttr("readonly");
        $('#id_last_name').removeAttr("readonly");
        $("#id_email").removeAttr("readonly");
        $("#myAccountInfoBtn").removeClass("hidden");
    }
}


//////////////////////////////////////
// Format Datetime for bootstrap table
//

function FormattedDate(input) {
    date = new Date(input);
    // Get year
    var year = date.getFullYear();

    // Get month
    var month = (1 + date.getMonth()).toString();
    month = month.length > 1 ? month : '0' + month;

    // Get day
    var day = date.getDate().toString();
    day = day.length > 1 ? day : '0' + day;

    // Get hours
    var hours = date.getHours();

    // AM PM
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours.toString();
    hours = hours.length > 1 ? hours: '0' + hours;
    hours = hours ? hours : 12; // the hour '0' should be '12'

    // Get minutes
    var minutes = date.getMinutes().toString();
    minutes = minutes < 10 ? '0'+minutes : minutes;
    minutes = minutes.length > 1 ? minutes: '0' + minutes;

    // Get seconds
    var seconds = date.getSeconds().toString();
    seconds = seconds.length > 1 ? seconds: '0' + seconds;

    return month + '/' + day + '/' + year + ' ' + hours + ':' + minutes +':'+seconds+ ' ' + ampm;
}
