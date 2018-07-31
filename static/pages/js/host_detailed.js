var rowIDSelected = null;
var apiurl = "/hosts/api/gethostbyid?id=";
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
function FillInfo(hostinfo) {
    if(hostinfo === undefined)
        $.get( geturl, function( data ) {
            $('#brHost').text(data.hostName);
            //  Fill in form
            $('#id_createBy').text(data.username);
            $("#id_dateCreated").text(DateTimeFormater(data.dateCreated));
            $("#id_dateUpdate").text(DateTimeFormater(data.dateUpdate));
            $('#id_id').val(data.id);
            $("#id_hostName").val(data.hostName);
            $("#id_ipAddr").val(data.ipAddr);
            $("#id_osName").val(data.osName);
            $("#id_osVersion").val(data.osVersion);
            $("#id_description").val(data.description);
            });
    else {
        $('#brHost').text(hostinfo.hostName);
        //  Fill in form
        $('#id_createBy').text(hostinfo.username);
        $("#id_dateCreated").text(DateTimeFormater(hostinfo.dateCreated));
        $("#id_dateUpdate").text(DateTimeFormater(hostinfo.dateUpdate));
        $('#id_id').val(hostinfo.id);
        $("#id_hostName").val(hostinfo.hostName);
        $("#id_ipAddr").val(hostinfo.ipAddr);
        $("#id_osName").val(hostinfo.osName);
        $("#id_osVersion").val(hostinfo.osVersion);
        $("#id_description").val(hostinfo.description);
    }
}

// Disable input until edit button is clicked
function SetReadonly(Enable) {
    if(Enable){
        $("#id_hostName").attr("readonly","readonly");
        $("#id_ipAddr").attr("readonly","readonly");
        $("#id_osName").attr("readonly","readonly");
        $("#id_osVersion").attr("readonly","readonly");
        $("#id_description").attr("readonly","readonly");
        $("#hostInfoBtn").addClass("hidden");
    }
    else{
        $("#id_hostName").removeAttr("readonly");
        $("#id_ipAddr").removeAttr("readonly");
        $("#id_osName").removeAttr("readonly");
        $("#id_osVersion").removeAttr("readonly");
        $("#id_description").removeAttr("readonly");
        $("#hostInfoBtn").removeClass("hidden");
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