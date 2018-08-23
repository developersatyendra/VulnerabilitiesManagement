var apiurl = "/projects/api/getprojectbyid?id=";

//////////////////////////////////////////////////
var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -2];
//////////////////////////////////////////////////
var geturl = apiurl.concat(id);

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
    $("#editProjectPostForm").submit(function(e){
        $.post("/projects/api/updateproject", $(this).serialize(), function(data){
            if(data.status != 0){
                $("#titleInfo").text("Error");
                $("#msgInfo").text("Error: "+data.message+'. '+ data.detail.name[0]);
            }
            else{
                $("#titleInfo").text("About");
                $("#msgInfo").text("The project is updated.");
                SetReadonly(true);

                // Dissable Save button
                $("#saveInfoBtn").attr('disabled', true);
            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
        }),


    //////////////////////////////////////////
    // Form on change
    //

    // Main Form
    $("#id_name").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $('#editProjectPostForm').change(function () {
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
                console.log(data);
                // Fill breadcrumb
                $('#brProject').text(data.object.name);

                //  Fill in form
                $('#id_name').val(data.object.name);
                $('#id_id').val(data.object.id);
                $('#id_createBy').val(data.object.username);
                $("#id_dateCreated").val(FormattedDate(data.object.createDate));
                $("#id_dateUpdate").val(FormattedDate(data.object.updateDate));
                $("#id_description").val(data.object.description);
                deferred.resolve(data);
            }
        });
    }
    else {
        // Fill breadcrumb
        $('#brScan').text(input.object.name);

        //  Fill in form
        $('#id_name').val(input.object.name);
        $('#id_id').val(input.object.id);
        $('#id_createBy').val(input.object.username);
        $("#id_dateCreated").val(FormattedDate(input.object.createDate));
        $("#id_dateUpdate").val(FormattedDate(input.object.updateDate));
        $("#id_description").val(input.object.description);
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

        $('#id_name').attr("readonly","readonly");
        $('#id_id').attr("readonly","readonly");
        $("#id_description").attr("readonly","readonly");
        $("#projectInfoBtn").addClass("hidden");
    }
    else{
        $('#id_name').removeAttr("readonly");
        $('#id_id').removeAttr("readonly");
        $("#id_description").removeAttr("readonly");
        $("#projectInfoBtn").removeClass("hidden");
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
