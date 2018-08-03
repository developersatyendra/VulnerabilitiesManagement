var rowIDSelected = null;
var apiurl = "/vuln/api/getvulnbyid?id=";
var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -1];
var geturl = apiurl.concat(id);
$(document).ready(
    FillInfo(),
    SetReadonly(true),

    // Click Edit button
    $("#edit").click(function () {
            SetReadonly(false)
        }),

    // Click Delete button
    $("#delete").click(function () {
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
                    $("#msgInfo").text("The host is deleted.");
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
            FillInfo();
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

            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
        })
);

// Fill in information of service
function FillInfo(vulninfo) {
    if(vulninfo === undefined)
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
            });
    else {
        $('#brVuln').text(vulninfo.name);
        //  Fill in form
        $('#id_name').val(vulninfo.name);
        $('#id_id').val(vulninfo.id);
        $("#id_levelRisk").val(vulninfo.levelRisk);
        $("#id_service").val(vulninfo.service.id);
        $("#id_cve").val(vulninfo.cve);
        $("#id_observation").val(vulninfo.observation);
        $("#id_recommendation").val(vulninfo.recommendation);
        $("#id_description").val(vulninfo.description);
    }
}

// Disable input until edit button is clicked
function SetReadonly(Enable) {
    if(Enable){
        $('#id_name').attr("readonly","readonly");
        $('#id_id').attr("readonly","readonly");
        $("#id_levelRisk").attr("readonly","readonly");
        $("#id_service").attr("readonly","readonly");
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
        $("#id_service").removeAttr("readonly");
        $("#id_cve").removeAttr("readonly");
        $("#id_observation").removeAttr("readonly");
        $("#id_recommendation").removeAttr("readonly");
        $("#id_description").removeAttr("readonly");
        $("#hostInfoBtn").removeClass("hidden");
    }
}
