var rowIDSelected = null;
var apiurl = "/vuln/api/getvulnbyid?id=";
var url = window.location.pathname;
var id = url.split("/")[2];
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

    // Click Edit button
    $("#edit").click(function () {
            SetReadonly(false)
        }),

    // Click Delete button
    $("#delete").click(function () {
        $("#msgOnDelete").text("Are you sure to delete this vulnerability?");
        $("#warningOnDeleteModal").modal("show");
    }),
    // Click Delete button from warning modal
    $("#confirmDelete").click(function () {
       // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');
        var ids = new Array();
        ids.push($("#id_id").val());
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('/vuln/api/deletevuln', $.param(data),
             function(data){
                if(data.status == 0){
                    $('#warningOnDeleteModal').modal('hide');
                    $("#titleInfo").text("About");
                    $("#msgInfo").text("The vulnerability is deleted.");
                    $("#infoModal").modal("show");
                    $("#infoModal").on('hidden.bs.modal', function (e) {
                          $( location ).attr("href", '/vuln');
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
    $("#cancelUpdateBtn").click(function () {
            if(flagDataStored){
                FillInfo(dataStored);
            }
            else{
                FillInfo();
            }
            SetReadonly(true);
    }),
    $("#editVulnPostForm").submit(function(e){
        $.post("/vuln/api/updatevuln", $(this).serialize(), function(data){
            if(data.status != 0){
                $("#titleInfo").text("Error");
                $("#msgInfo").text("Error: "+data.message+'. '+ data.detail.name[0]);
            }
            else{
                $("#titleInfo").text("About");
                $("#msgInfo").text("The host is updated.");
                SetReadonly(true);
            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
    }),

    //////////////////////////////////////////
    // Form on change
    //

    // Main Form
    $('#editVulnPostForm').change(function () {
        $('#saveInfoBtn').attr('disabled', false);
    }),
    $("#id_name").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_levelRisk").on("input", function(){
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_cve").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_observation").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_recommendation").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    })
);

// Fill in information of service
function FillInfo(input) {
    flagDataStored = false;
    var deferred = new $.Deferred();
    if(input === undefined)
        $.get( geturl, function( data ) {
            $('#brVuln').text(data.name);
            //  Fill in form
            $('#id_name').val(data.name);
            $('#id_id').val(data.id);
            $("#id_levelRisk").val(data.levelRisk);
            $("#id_service").val(data.service.id);
            $("#id_cve").val(data.cve);
            $("#id_observation").val(data.observation);
            $("#id_recommendation").val(data.recommendation);
            $("#id_description").val(data.description);
            deferred.resolve(data);
            });
    else {
        $('#brVuln').text(input.name);
        //  Fill in form
        $('#id_name').val(input.name);
        $('#id_id').val(input.id);
        $("#id_levelRisk").val(input.levelRisk);
        $("#id_service").val(input.service.id);
        $("#id_cve").val(input.cve);
        $("#id_observation").val(input.observation);
        $("#id_recommendation").val(input.recommendation);
        $("#id_description").val(input.description);
        deferred.resolve(input);
    }
    return deferred.promise();
}

// Disable input until edit button is clicked
function SetReadonly(Enable) {
    if(Enable){
        // Disable Save Update button
        $("#saveInfoBtn").attr('disabled', true);

        $('#id_name').attr("readonly","readonly");
        $('#id_id').attr("readonly","readonly");
        $("#id_levelRisk").attr("readonly","readonly");
        $("#id_service").attr("disabled", true);
        $("#id_cve").attr("readonly","readonly");
        $("#id_observation").attr("readonly","readonly");
        $("#id_recommendation").attr("readonly","readonly");
        $("#id_description").attr("readonly","readonly");
        $("#hostInfoBtn").addClass("hidden");
    }
    else{
        $('#id_name').removeAttr("readonly");
        $('#id_id').removeAttr("readonly");
        $("#id_levelRisk").removeAttr("readonly");
        $("#id_service").attr("disabled", false);
        $("#id_cve").removeAttr("readonly");
        $("#id_observation").removeAttr("readonly");
        $("#id_recommendation").removeAttr("readonly");
        $("#id_description").removeAttr("readonly");
        $("#hostInfoBtn").removeClass("hidden");
    }
}
