var rowIDSelected = null;
var apiurl = "/services/api/getservicebyid?id=";
var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -2];
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

    //////////////////////////////////////
    // Click Edit button
    //
    $("#edit").click(function () {
            SetReadonly(false)
        }),

    //////////////////////////////////////
    // Click Delete button
    //
    $("#delete").click(function () {
        $("#warningOnDeleteModal").modal("show");
    }),

    //////////////////////////////////////
    // Click Delete button from warning modal
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');
        var ids = new Array();
        ids.push($("#id_id").val());
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('../api/deleteservice', $.param(data),
             function(data){
                if(data.status == 0){
                    $('#warningOnDeleteModal').modal('hide');
                    $("#titleInfo").text("About");
                    $("#msgInfo").text("The service is deleted.");
                    $("#infoModal").modal("show");
                    $("#infoModal").on('hidden.bs.modal', function (e) {
                          $( location ).attr("href", '/services');
                    });
                }
                else{
                    $('#warningOnDeleteModal').modal('hide');
                    $("#titleInfo").text("Error");
                    $("#msgInfo").text("Error: "+data.message+'. '+ data.detail.__all__[0]);
                    $("#infoModal").modal("show");
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),
    $("#cancelUpdateBtn").click(function () {
        if(flagDataStored){
            FillInfo(dataStored);
        }
        else{
            FillInfo();
        }
        SetReadonly(true);
    }),
    $("#editServicePostForm").submit(function(e){
        $.post("../api/updateservice", $(this).serialize(), function(data){
            var notification = $("#retMsgEdit");
            if(data.status != 0){
                $("#titleInfo").text("Error");
                $("#msgInfo").text("Error: "+data.message+'. '+ data.detail.__all__[0]);
            }
            else{
                $("#titleInfo").text("About");
                $("#msgInfo").text("The service is updated.");
                SetReadonly(true);
            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
    }),

    //////////////////////////////////////////
    // Form on change to enable submit buttons
    //
    $('#editServicePostForm').change(function () {
        $('#saveInfoBtn').attr('disabled', false);
    }),
    $("#id_name").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_port").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    })
);

//////////////////////////////////////
// Fill in information of service
//
function FillInfo(input) {
    flagDataStored = false;
    var deferred = new $.Deferred();
    if(input === undefined)
        $.get( geturl, function( data ) {
            $('#brService').text(data.name);
            //  Fill in form
            $('#id_id').val(data.id);
            $('#id_createBy').val(data.username);
            $("#id_dateCreated").val(FormattedDate(data.dateCreated));
            $("#id_dateUpdate").val(FormattedDate(data.dateUpdate));
            $("#id_name").val(data.name);
            $("#id_port").val(data.port);
            $("#id_description").val(data.description);
            deferred.resolve(data);
            });
    else {
        $('#brService').text(input.name);
        //  Fill in form
        $('#id_id').val(input.id);
        $('#id_createBy').val(input.username);
        $("#id_dateCreated").val(FormattedDate(input.dateCreated));
        $("#id_dateUpdate").val(FormattedDate(input.dateUpdate));
        $("#id_name").val(input.name);
        $("#id_port").val(input.port);
        $("#id_description").val(input.description);
        deferred.resolve(input);
    }
    return deferred.promise();
}

//////////////////////////////////////
// Disable input until edit button is clicked
//
function SetReadonly(Enable) {
    if(Enable){
        $("#id_name").attr("readonly","readonly");
        $("#id_port").attr("readonly","readonly");
        $("#id_description").attr("readonly","readonly");
        $("#serviceInfoBtn").addClass("hidden");

        // Dissable Save button
        $("#saveInfoBtn").attr('disabled', true);
    }
    else{
        $("#id_name").removeAttr("readonly");
        $("#id_port").removeAttr("readonly");
        $("#id_description").removeAttr("readonly");
        $("#serviceInfoBtn").removeClass("hidden");
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