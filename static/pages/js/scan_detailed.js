var rowIDSelected = null;
var apiurl = "/scans/api/getscanbyid?id=";
var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -1];
var geturl = apiurl.concat(id);
$(document).ready(
    //
    // Initial datetime picker
    //
    $('#dpStartTime').datetimepicker({
        format: 'MM/DD/YYYY hh:mm:ss A',
        sideBySide: true
        }),
    $('#dpEndTime').datetimepicker({
        format: 'MM/DD/YYYY hh:mm:ss A',
        sideBySide: true
        }),
    //
    // Fill data from datetimepicker to form
    //
    $("#dpStartTime").on('dp.change', function(e){
        var date = e.date.toISOString();
        $('#id_startTime').val(date);
    }),
    $("#dpEndTime").on('dp.change', function(e){
        var date = e.date.toISOString();
        $('#id_endTime').val(date);
    }),
    FillInfo(),
    SetReadonly(true),
    SetReadonlyAttachment(true),

    //////////////////////////////////////////
    // Click Edit button
    //
    $("#edit").click(function () {
            SetReadonly(false)
        }),
    $("#editAtt").click(function () {
        SetReadonlyAttachment(false);
    }),

    //////////////////////////////////////////
    // Click Delete button
    //
    $("#delete").click(function () {
        $("#warningOnDeleteModal").modal("show");
    }),

    //////////////////////////////////////////
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
        $.post('/scans/api/deletescan', $.param(data),
             function(data){
                if(data.status == 0){
                    $('#warningOnDeleteModal').modal('hide');
                    $("#titleInfo").text("About");
                    $("#msgInfo").text("The scan task is deleted.");
                    $("#infoModal").modal("show");
                    $("#infoModal").on('hidden.bs.modal', function (e) {
                          $( location ).attr("href", '/scans');
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
            FillInfo();
            SetReadonly(true);
        }),

    //////////////////////////////////////////
    // POST update
    //
    $("#editScanPostForm").submit(function(e){
        $.post("/scans/api/updatescan", $(this).serialize(), function(data){
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
    // Click Browse
    //
    $("#btnBrowseAtt").click( function () {
        $("#id_fileAttachment").trigger('click');
        }
    ),

    //////////////////////////////////////////
    // Click attachment text input
    //
    $("#fileAtt").click( function () {
        $("#id_fileAttachment").trigger('click');
        }
    ),

    //////////////////////////////////////////
    // Show file path on text input
    //
    $("#id_fileAttachment").change( function (e) {
        filename = $(this).val().replace(/\\/g, '/').replace(/.*\//, '');
        $("#fileAtt").val(filename)
        }
    )
);

//////////////////////////////////////////
// Fill in information of service
//
function FillInfo(scaninfo) {
    if(scaninfo === undefined)
        $.get( geturl, function( data ) {
            $('#brScan').text(data.name);
            //  Fill in form
            $('#id_name').val(data.name);
            $('#id_id').val(data.id);
            $('#id_submitter').val(data.username);
            $("#id_dateCreated").val(DateTimeFormater(data.dateCreated));
            $("#id_dateUpdate").val(DateTimeFormater(data.dateUpdate));
            $("#dpStartTime").data("DateTimePicker").date(new Date(data.startTime));
            $("#dpEndTime").data("DateTimePicker").date(new Date(data.endTime));
            $("#id_scanProject").val(data.scanProject.id);
            $("#id_isProcessed").val(data.isProcessed);
            $("#id_description").val(data.description);
            $("id_fileAttachment").val(data.fileAttachment);
            });
    else {
        $('#brScan').text(scaninfo.name);
        //  Fill in form
        $('#id_name').val(scaninfo.name);
        $('#id_id').val(scaninfo.id);
        $('#id_submitter').val(scaninfo.username);
        $("#id_dateCreated").val(DateTimeFormater(scaninfo.dateCreated));
        $("#id_dateUpdate").val(DateTimeFormater(scaninfo.dateUpdate));
        $("#dpStartTime").data("DateTimePicker").date(new Date(scaninfo.startTime));
        $("#dpEndTime").data("DateTimePicker").date(new Date(data.endTime));
        $("#id_scanProject").val(scaninfo.scanProject.id);
        $("#id_isProcessed").val(scaninfo.isProcessed);
        $("#id_description").val(scaninfo.description);
        $("id_fileAttachment").val(scaninfo.fileAttachment);
    }
}

//////////////////////////////////////////
// Disable input until edit button is clicked
//
function SetReadonly(Enable) {
    if(Enable){
        $('#id_name').attr("readonly","readonly");
        $('#id_id').attr("readonly","readonly");
        $("#dpStartTime").data("DateTimePicker").disable();
        $("#dpEndTime").data("DateTimePicker").disable();

        $("#id_scanProject").attr('disabled', true);
        $("#id_isProcessed").attr('disabled', true);
        $("#id_description").attr("readonly","readonly");
        $("#scanInfoBtn").addClass("hidden");
    }
    else{
        $('#id_name').removeAttr("readonly");
        $('#id_id').removeAttr("readonly");
        $("#dpStartTime").data("DateTimePicker").enable();
        $("#dpEndTime").data("DateTimePicker").enable();

        $("#id_scanProject").attr('disabled', false);
        $("#id_isProcessed").attr('disabled', false);
        $("#id_description").removeAttr("readonly");
        $("#scanInfoBtn").removeClass("hidden");
    }
}

//////////////////////////////////////////
// Disable input of attachment until edit button is clicked
//
function SetReadonlyAttachment(Enable) {
    if(Enable){
        $("#btnBrowseAtt").attr('disabled', true);
        $("#fileAtt").attr('disabled', true);
        $("#btnDownloadAtt").attr('disabled', false);
        $("#scanAttBtn").addClass("hidden");
    }
    else{
        $("#btnBrowseAtt").attr('disabled', false);
        $("#fileAtt").attr('disabled', false);
        $("#btnDownloadAtt").attr('disabled', true);
        $("#scanAttBtn").removeClass("hidden");
    }
}

//////////////////////////////////////////
// Format Datetime for bootstrap table
//
function DateTimeFormater(value, row, index) {
    date_t = new Date(value);
    return date_t.toLocaleString();
}