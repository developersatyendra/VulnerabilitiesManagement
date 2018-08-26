var rowIDSelected = null;
$(document).ready(
    //////////////////////////////////////////
    // Decleare scan tasks table
    //
    $(function () {
        $("#scanstable").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    title: "Scan Task",
                    field: "name",
                    align: "center",
                    valign: "middle",
                    formatter: HrefFormater,
                    sortable: true
                },
                {
                    title: "Is Processed",
                    field: "isProcessed",
                    align: "center",
                    valign: "middle",
                    formatter: BooleanFormatter,
                    sortable: true
                },
                {
                    title: "Start Time",
                    field: "startTime",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    sortable: true
                },
                {
                    title: "Finished Time",
                    field: "endTime",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    sortable: true
                },
                {
                    title: "Scan Project",
                    field: "scanProject.name",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                  title: "Description",
                  field: "description",
                  align: "center",
                  valign: "middle",
                  sortable: true
                }
            ],
            // url: "/scans/api/getscans",
            // method: "get",
            ajax: ajaxRequest,
            idField: "id",
            queryParamsType: "",
            striped: true,
            pagination: true,
            sidePagination: "server",
            pageList: [5, 10, 20, 50, 100, 200, 'All'],
            search: true,
        })
    }),

    //////////////////////////////////////////
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
    $('#dpEditStartTime').datetimepicker({
        format: 'MM/DD/YYYY hh:mm:ss A',
        sideBySide: true
        }),
    $('#dpEditEndTime').datetimepicker({
        format: 'MM/DD/YYYY hh:mm:ss A',
        sideBySide: true
        }),

    //////////////////////////////////////////
    // Fill data from datetimepicker to form
    //
    $("#dpEditStartTime").on('dp.change', function(e){
        var date = e.date.toISOString();
        $('#id_startTime_edit').val(date);
    }),
    $("#dpEditEndTime").on('dp.change', function(e){
        var date = e.date.toISOString();
        $('#id_endTime_edit').val(date);
    }),
    $("#dpStartTime").on('dp.change', function(e){
        var date = e.date.toISOString();
        $('#id_startTime').val(date);
    }),
    $("#dpEndTime").on('dp.change', function(e){
        var date = e.date.toISOString();
        $('#id_endTime').val(date);
    }),

    //////////////////////////////////////////
    // Edit scanning task
    //
    $("#editScanPostForm").submit(function(e){
        var data = $('#editScanPostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updatescan", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                var errStr = "Error: "+data.message;
                if(typeof data.detail.name !='undefined'){
                    errStr = errStr + ". Name: " + data.detail.name[0];
                }
                if(typeof data.detail.startTime !='undefined'){
                    errStr = errStr + ". Start Time: " + data.detail.startTime[0];
                }
                if(typeof data.detail.endTime !='undefined'){
                    errStr = errStr + ". Finished Time: " + data.detail.endTime[0];
                }
                notification.html(errStr);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("The vulnerability is updated.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");

                // Disable Save button
                $("#saveEditBtn").attr('disabled', true);
            }
            notification.append(closebtn);
            $("#scanstable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editScanModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //////////////////////////////////////////
    // Add New scan
    //
    $("#addScanPostForm").submit(function(e){
        var formData = new FormData(this);
        $.ajax({
            url: "./api/addscan",
            type: 'POST',
            data: formData,
            success: function (data) {
                var notification = $("#retMsgAdd");
                var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
                notification.removeClass("hidden");
                if(data.status != 0){
                    var errStr = "Error: "+data.message;
                    if(typeof data.detail.name !='undefined'){
                    errStr = errStr + ". Name: " + data.detail.name[0];
                    }
                    if(typeof data.detail.startTime !='undefined'){
                        errStr = errStr + ". Start Time: " + data.detail.startTime[0];
                    }
                    if(typeof data.detail.endTime !='undefined'){
                        errStr = errStr + ". Finished Time: " + data.detail.endTime[0];
                    }
                    notification.html(errStr);
                    notification.removeClass("alert-info");
                    notification.addClass("alert-danger");
                }
                else{
                    notification.html("New vulnerability is added.");
                    notification.removeClass("alert-danger");
                    notification.addClass("alert-info");

                    // Disable Save button
                    $("#saveAddBtn").attr('disabled', true);
                }
                notification.append(closebtn);
                $("#scanstable").bootstrapTable('refresh');
            },
            cache: false,
            contentType: false,
            processData: false
        });
        e.preventDefault();
    }),
    $("#addScanModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //////////////////////////////////////////
    // Confirm delete scan tasks
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains vuln ids
        var dataTable = $("#scanstable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deletescan', $.param(data),
             function(returnedData){
                if(returnedData.status == 0){
                    $('#warningOnDelete').modal('hide');
                    $("#scanstable").bootstrapTable('refresh');

                    $('#msgInfo').text(returnedData.message);
                    $('#infoModal').modal('show');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //////////////////////////////////////////
    // show delete scan tasks warning
    //
    $("#delete").click(function () {
        var data = $("#scanstable").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected scan task?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected scan tasks?");
            }
            $('#warningOnDelete').modal('show')
        }
    }),

    //////////////////////////////////////////
    // Fill in edit form when edit btn is clicked
    //
    $("#edit").click(function () {
        var data = $("#scanstable").bootstrapTable('getSelections');
        if(data.length > 1){
            $('#msgInfo').text("Please choose only one row for editing.");
            $('#infoModal').modal('show');
        }
        else if (data.length == 1) {
            $('#id_name_edit').val(data[0].name);
            $('#id_isProcessed_edit').val(data[0].isProcessed);
            var startTime = data[0].startTime;
            var endTime = data[0].endTime;

            $('#id_fileAttachment_edit').val(data[0].fileAttachment);
            $('#id_scanProject_edit').val(data[0].scanProject.id);
            $('#id_description_edit').val(data[0].description);
            $('#editScanModal').modal('show');
            $("#dpEditStartTime").data("DateTimePicker").date(new Date(data[0].startTime));
            $("#dpEditEndTime").data("DateTimePicker").date(new Date(data[0].endTime));
            rowIDSelected = data[0].id;

            // Dissable Save Edit Button
            $("#saveEditBtn").attr('disabled', true);
        }
    }),

    //////////////////////////////////////////
    // Detect changes on Select row to enable or disable Delete/ Edit button
    //
    $("#scanstable").change(function () {
        var data = $("#scanstable").bootstrapTable('getSelections');
        var editBtn = $("#edit");
        var delBtn = $("#delete");
        if(data.length!=1){
            editBtn.addClass("disabled");
        }
        else{
            editBtn.removeClass("disabled");
        }
        if(data.length==0 ){
            delBtn.addClass("disabled");
        }
        else{
            delBtn.removeClass("disabled");
        }
    }),

    //////////////////////////////////////////
    // When the close does. Hide it instead of remove it with Dom
    //
    $('.alert').on('close.bs.alert', function (e) {
        $(this).addClass("hidden");
        e.preventDefault();
    }),

    //////////////////////////////////////////
    // Form on change to enable submit buttons
    //

    // Add form
    $('#addScanPostForm').change(function () {
        $('#saveAddBtn').attr('disabled', false);
    }),
    $("#id_name").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#dpStartTime").on('dp.change', function(){
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#dpEndTime").on('dp.change', function(){
        $("#saveAddBtn").attr('disabled', false);
    }),

    // Edit form
    $('#editScanPostForm').change(function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_name_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_description_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#dpEditStartTime").on('dp.change', function(){
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#dpEditEndTime").on('dp.change', function(){
        $("#saveEditBtn").attr('disabled', false);
    })
);

// Format href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="' + row.id + '"> ' + row.name +'</a>';
}

// Format Datetime for bootstrap table
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

// Boolean Formatter for Tables
function BooleanFormatter(value, row, index){
    if(value){
        return '<b><i class="fa fa-check" aria-hidden="true"></i></b>';
    }
    else
        return '<b><i class="fa fa-remove" aria-hidden="true"></i></i></b>';
}

//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/scans/api/getscans",
        data: params.data,
        dataType: "json",
        success: function(data) {
            if(data.status == 0){
                params.success({
                    "rows": data.object.rows,
                    "total": data.object.total
                })
            }
        },
       error: function (er) {
            params.error(er);
        }
    });
}