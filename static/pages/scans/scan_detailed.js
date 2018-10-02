var apiurl = "/scans/api/getscanbyid?id=";
var apiattachment = "/scans/api/getattachment?id=";

//////////////////////////////////////////////////
var url = window.location.pathname;
var id = url.split("/")[2];
console.log(url.split("/"));
//////////////////////////////////////////////////
var geturl = apiurl.concat(id);
var getAttachment = apiattachment.concat(id);

//////////////////////////////////////////////////
//Set to 0 to delete scantask
//Set to 1 to delete attachment
var flagDeleteOption = -1 ;

//////////////////////////////////////////////////
var flagDataStored = false;
var dataStored;
var flagAttachmentStore = false;
var dataAttachmentStored;
$(document).ready(
    //////////////////////////////////////////////////
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

    //////////////////////////////////////////////////
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

    //////////////////////////////////////////////////
    // Fill data to forms and set them to readonly state
    //
    $.when(FillInfo()).done(function (result) {
        dataStored = result;
        flagDataStored = true;
    }),
    $.when(FillInfoAttachment()).done(function (result) {
        dataAttachmentStored = result;
        flagAttachmentStore = true;
    }),
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
        flagDeleteOption = 0;
        $('#msgOnDelete').text("Are you sure to delete this scan task?");
        $("#warningOnDeleteModal").modal("show");
    }),
    $("#deleteAtt").click(function () {
        flagDeleteOption = 1;
        $('#msgOnDelete').text("Are you sure to delete this attachment of scan task?");
        $("#warningOnDeleteModal").modal("show");
    }),
    //////////////////////////////////////////
    // Click Delete button from warning modal
    //
    $("#confirmDelete").click(function () {
        var csrf_token = $('meta[name="csrf-token"]').attr('content');
        var data = [];
        if(flagDeleteOption==0){
            // Get csrf_token

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
        }
        else if(flagDeleteOption==1){
            var id = $("#editAttachmentForm input[name='id']").val();
            data.push({name: "id", value: id});
            data.push({name: "csrfmiddlewaretoken", value: csrf_token});
            $.post('/scans/api/deleteattachment', $.param(data),
                function(data){
                    if(data.status == 0){
                        console.log(data);
                        $('#warningOnDeleteModal').modal('hide');
                        $("#titleInfo").text("About");
                        $("#msgInfo").text("The attachment of scan task is deleted.");
                        $("#infoModal").modal("show");
                        $("#infoModal").on('hidden.bs.modal', function (e) {
                               $("#fileAtt").val(null);
                               $("#fileAtt").trigger('change');
                        });
                    }
                    else{
                        $('#warningOnDeleteModal').modal('hide');
                        $("#titleInfo").text("Error");
                        $("#msgInfo").text("Error: "+data.message+'.');
                        $("#infoModal").modal("show");
                    }
            }, 'json');
            $('#warningOnDelete').modal('hide')
        }

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

    $("#cancelAttBtn").click(function () {
        if(flagAttachmentStore){
            FillInfoAttachment(dataAttachmentStored);
        }
        else{
            FillInfoAttachment();
        }
        SetReadonlyAttachment(true);
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
                $("#msgInfo").text("The scan task is updated.");
                SetReadonly(true);
            }
            $("#infoModal").modal("show");
        });
        e.preventDefault();
        }),

    //////////////////////////////////////////
    // POST Attachment update
    //
    $("#editAttachmentForm").submit(function(e){
        var formData = new FormData(this);
        $.ajax({
            url: "/scans/api/addattachment",
            type: 'POST',
            data: formData,
            success: function (data) {
                if(data.status != 0){
                    $("#titleInfo").text("Error");
                    var error = "Error: "+data.message;
                    if(typeof data.detail.id !='undefined'){
                        error += '. '+ data.detail.id[0];
                    }
                    if(typeof data.detail.fileAttachment !='undefined'){
                        error += '. '+ data.detail.fileAttachment[0];
                    }
                    $("#msgInfo").text(error);
                }
                else{
                    $("#titleInfo").text("About");
                    $("#msgInfo").text("The attachment is successfully uploaded.");
                    SetReadonlyAttachment(true);
                    FillInfoAttachment();
                }
                $("#infoModal").modal("show");
            },
            cache: false,
            contentType: false,
            processData: false
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
    // Click Download
    //
    $("#btnDownloadAtt").click(function () {
        if($("#fileAtt").val() !=''){
            window.open($(this).attr('download'));
        }

    }),

    //////////////////////////////////////////
    // Click attachment text input
    //
    $("#fileAtt").click( function () {
        $("#id_fileAttachment").trigger('click');
        }
    ),

    ////////////////////////////////////////
    //Disable btnDownloadAtt if fileAtt is empty
    //
    $("#fileAtt").change(function (e) {
        if($(this).val()!=''){
            $("#btnDownloadAtt").attr('disabled', false);
        }
        else{
            $("#btnDownloadAtt").attr('disabled', true);
        }
    }),

    //////////////////////////////////////////
    // Show file path on text input
    //
    $("#id_fileAttachment").change(function (e) {
            $("#fileAtt").val(GetFileName($(this).val()));
        }
    ),

    //////////////////////////////////////////
    // Form on change
    //

    // Main Form
    $("#dpStartTime").on('dp.change', function(){
        if(flagDataStored) {
            var startTimeStore = FormattedDate(new Date(dataStored.startTime));
            var dpStartTime = $(this).find("input").val();
            if (startTimeStore != dpStartTime)
                $("#saveInfoBtn").attr('disabled', false);
        }
    }),
    $("#dpEndTime").on('dp.change', function(){
        if(flagDataStored){
            var endTimeStore = FormattedDate(new Date(dataStored.endTime));
            var dpEndTime = $(this).find("input").val();
            if(endTimeStore!= dpEndTime)
                $("#saveInfoBtn").attr('disabled', false);
        }
    }),
    $("#id_name").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),
    $('#editScanPostForm').change(function () {
        $("#saveInfoBtn").attr('disabled', false);
    }),

    // Attachment Form
    $('#editAttachmentForm').change(function () {
        $('#uploadAttBtn').attr('disabled', false);
    })
);

//////////////////////////////////////////
// Fill in information of scan task
//
function FillInfo(scaninfo) {
    flagDataStored = false;
    var deferred = new $.Deferred();
    if(scaninfo === undefined) {
        $.ajax({
            type: "GET",
            url: geturl,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {

                // Fill breadcrumb
                $('#brScan').text(data.name);

                //  Fill in form
                $('#id_name').val(data.name);
                $('#id_id').val(data.id);
                $('#id_submitter').val(data.username);
                $("#id_dateCreated").val(FormattedDate(data.dateCreated));
                $("#id_dateUpdate").val(FormattedDate(data.dateUpdate));
                $("#dpStartTime").data("DateTimePicker").date(new Date(data.startTime));
                $("#dpEndTime").data("DateTimePicker").date(new Date(data.endTime));
                $("#id_scanProject").val(data.scanProject.id);
                $('#id_isProcessed').prop('checked', data.isProcessed);
                $("#id_description").val(data.description);
                $("id_fileAttachment").val(data.fileAttachment);
                deferred.resolve(data);
            }
        });
    }
    else {
        // Fill breadcrumb
        $('#brScan').text(scaninfo.name);

        //  Fill in form
        $('#id_name').val(scaninfo.name);
        $('#id_id').val(scaninfo.id);
        $('#id_submitter').val(scaninfo.username);
        $("#id_dateCreated").val(FormattedDate(scaninfo.dateCreated));
        $("#id_dateUpdate").val(FormattedDate(scaninfo.dateUpdate));
        $("#dpStartTime").data("DateTimePicker").date(new Date(scaninfo.startTime));
        $("#dpEndTime").data("DateTimePicker").date(new Date(scaninfo.endTime));
        $("#id_scanProject").val(scaninfo.scanProject.id);
        $("#id_isProcessed").prop('checked', scaninfo.isProcessed);
        $("#id_description").val(scaninfo.description);
        $("id_fileAttachment").val(scaninfo.fileAttachment);
        deferred.resolve(scaninfo);
    }
    return deferred.promise();
}

//////////////////////////////////////////
// Fill in attachment information of service
//
function FillInfoAttachment(scaninfo) {
    var deferred = new $.Deferred();
    var fileAtt = $("#fileAtt");
    flagAttachmentStore = false;
    if(scaninfo === undefined){
        $.ajax({
            type: "GET",
            url: getAttachment,
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            success: function (data) {
                fileAtt.val(GetFileName(data.fileAttachment));
                $("#editAttachmentForm input[name='id']").val(data.id);
                $("#btnDownloadAtt").attr("download", data.fileAttachment);

                //Disable btnDownloadAtt if fileAtt is empty
                if(data.fileAttachment==''||data.fileAttachment==null){
                    $("#btnDownloadAtt").attr('disabled', true);
                }
                else{
                    $("#btnDownloadAtt").attr('disabled', false);
                }
                deferred.resolve(data);
            }
        });
    }
    else{
        fileAtt.val(GetFileName(scaninfo.fileAttachment));
        $('#id_id').val(scaninfo.id);

        //Disable btnDownloadAtt if fileAtt is empty
        if(scaninfo.fileAttachment==''||scaninfo.fileAttachment==null){
            $("#btnDownloadAtt").attr('disabled', true);
        }
        else{
            $("#btnDownloadAtt").attr('disabled', false);
        }
        deferred.resolve(scaninfo);
    }
    return deferred.promise();
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

        // Dissable Save button
        $("#saveInfoBtn").attr('disabled', true);
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
        // $("#btnDownloadAtt").attr('disabled', false);
        $("#scanAttBtn").addClass("hidden");

        // Disable Upload Button
        $('#uploadAttBtn').attr('disabled', true);
    }
    else{
        $("#btnBrowseAtt").attr('disabled', false);
        $("#fileAtt").attr('disabled', false);
        // $("#btnDownloadAtt").attr('disabled', true);
        $("#scanAttBtn").removeClass("hidden");
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

function GetFileName(filepath) {
    if(filepath!==null){
        var fileNameIndex = filepath.lastIndexOf("/") + 1;
        var fileNameIndexWindows = filepath.lastIndexOf("\\") + 1;
        var filename = '';
        if(fileNameIndex != 0){
            filename =  filepath.substr(fileNameIndex);
        }
        else if(fileNameIndexWindows !=0){
            filename =  filepath.substr(fileNameIndexWindows);
        }
        else {
            return "";
        }
        return filename;
    }
    return "";
}