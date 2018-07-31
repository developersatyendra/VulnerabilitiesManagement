var rowIDSelected = null;
var apiurl = "/services/api/getservicebyid?id=";
var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -2];
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
            FillInfo();
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

            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
        })
);

// Fill in information of service
function FillInfo(serviceinfo) {
    if(serviceinfo === undefined)
        $.get( geturl, function( data ) {
            $('#brService').text(data.name);
            //  Fill in form
            $('#id_id').val(data.id);
            $('#id_createBy').text(data.username);
            $("#id_dateCreated").text(DateTimeFormater(data.dateCreated));
            $("#id_dateUpdate").text(DateTimeFormater(data.dateUpdate));
            $("#id_name").val(data.name);
            $("#id_port").val(data.port);
            $("#id_description").val(data.description);
            });
    else {
        $('#brService').text(serviceinfo.name);
        //  Fill in form
        $('#id_id').val(serviceinfo.id);
        $('#id_createBy').text(serviceinfo.username);
        $("#id_dateCreated").text(DateTimeFormater(serviceinfo.dateCreated));
        $("#id_dateUpdate").text(DateTimeFormater(serviceinfo.dateUpdate));
        $("#id_name").val(serviceinfo.name);
        $("#id_port").val(serviceinfo.port);
        $("#id_description").val(serviceinfo.description);
    }
}

// Disable input until edit button is clicked
function SetReadonly(Enable) {
    if(Enable){
        $("#id_name").attr("readonly","readonly");
        $("#id_port").attr("readonly","readonly");
        $("#id_description").attr("readonly","readonly");
        $("#serviceInfoBtn").addClass("hidden");
    }
    else{
        $("#id_name").removeAttr("readonly");
        $("#id_port").removeAttr("readonly");
        $("#id_description").removeAttr("readonly");
        $("#serviceInfoBtn").removeClass("hidden");
    }
}

// Format Datetime for bootstrap table
function DateTimeFormater(value, row, index) {
    date_t = new Date(value);
    return date_t.toLocaleString();
}

// Format Href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a id="delete" href="' + row.id + '"> ' + row.name +'</a>';
}