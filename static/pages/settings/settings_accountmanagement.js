var rowIDSelected = null;
const PERMS_VIEWONLY = 0;
const PERMS_SUBMITTER = 1;
const PERMS_MANAGER = 2;
$(document).ready(
    //////////////////////////////////////////
    // Decleare scan tasks table
    //
    $(function () {
        $("#datatable").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    title: "Username",
                    field: "username",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "First Name",
                    field: "first_name",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Last Name",
                    field: "last_name",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },

                {
                    title: "Email",
                    field: "email",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Date Joined",
                    field: "date_joined",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    sortable: true
                },
                {
                    title: "Active",
                    field: "is_active",
                    align: "center",
                    valign: "middle",
                    formatter: BooleanFormatter,
                    sortable: true
                },
                {
                    title: "Super User",
                    field: "is_superuser",
                    align: "center",
                    valign: "middle",
                    formatter: BooleanFormatter,
                    sortable: true
                },
                {
                    title: "Permission",
                    field: "permissionLevel",
                    align: "center",
                    valign: "middle",
                    formatter: PermissionFormatter,
                    sortable: true
                }
            ],
            ajax: ajaxRequest,
            queryParamsType: "",
            idField: "id",
            striped: true,
            pagination: true,
            sidePagination: "server",
            pageList: [5, 10, 20, 50, 100, 200, 'All'],
            search: true,
        })
    }),

    //////////////////////////////////////////
    // Initial

    //////////////////////////////////////////
    // Add New Account
    //
    $("#addUserPostForm").submit(function(e){
        var formData = new FormData(this);
        $.ajax({
            url: "/accounts/api/createaccount",
            type: 'POST',
            data: formData,
            success: function (data) {
                var notification = $("#retMsgAdd");
                var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
                notification.removeClass("hidden");
                if(data.status != 0){
                    var errStr = "Error: "+data.message;
                    notification.html(errStr);
                    notification.removeClass("alert-info");
                    notification.addClass("alert-danger");
                    for(var prop in data.detail){
                    if(prop === "username"){
                        $('#id_username').parent().addClass("has-error");
                        $('#id_username').next().text(data.detail.name[0]);
                    }
                    else if(prop === "host"){
                        $('#id_scanProject').parent().addClass("has-error");
                        $('#id_scanProject').next("span").text(data.detail.host[0]);
                    }
                    else if(prop === "format"){
                        $('#id_format').parent().addClass("has-error");
                        $('#id_format').next("span").text(data.detail.format[0]);
                    }
                }
                }
                else{
                    notification.html("New account is added.");
                    notification.removeClass("alert-danger");
                    notification.addClass("alert-info");

                    // Disable Save button
                    $("#saveAddBtn").attr('disabled', true);
                }
                notification.append(closebtn);
                $("#datatable").bootstrapTable('refresh');
            },
            cache: false,
            contentType: false,
            processData: false
        });
        e.preventDefault();
    }),
    $("#addUserModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
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
        var data = $("#datatable").bootstrapTable('getSelections');
        if(data.length > 1){
            $('#msgInfo').text("Please choose only one row for editing.");
            $('#infoModal').modal('show');
        }
        else if (data.length == 1) {
            $('#id_username_edit').val(data[0].username);
            $('#id_first_name_edit').val(data[0].first_name);
            $('#id_last_name_edit').val(data[0].last_name);
            $('#id_email_edit').val(data[0].email);
            $('#id_permission_edit').val(data[0].permissionLevel);
            if(data[0].state)
                $('#id_isActive_edit').val(0);
            else
                $('#id_isActive_edit').val(1);;
            $('#editUserModal').modal('show');
            rowIDSelected = data[0].id;

            // Dissable Save Edit Button
            $("#saveEditBtn").attr('disabled', true);
        }
    }),

    //////////////////////////////////////////
    // Fill in reset form when reset btn is clicked
    //
    $("#reset").click(function () {
        var data = $("#datatable").bootstrapTable('getSelections');
        if(data.length > 1){
            $('#msgInfo').text("Please choose only one row for editing.");
            $('#infoModal').modal('show');
        }
        else if (data.length == 1) {
            $('#id_username_reset').val(data[0].username);
            $('#resetPasswordModal').modal('show');
            rowIDSelected = data[0].id;

            // Dissable Save Edit Button
            $("#saveResetBtn").attr('disabled', true);
        }
    }),


    //////////////////////////////////////////
    // Detect changes on Select row to enable or disable Delete/ Edit button
    //
    $("#datatable").change(function () {
        var data = $("#datatable").bootstrapTable('getSelections');
        var editBtn = $("#edit");
        var delBtn = $("#delete");
        var resetBtn = $("#reset")
        if(data.length!=1){
            editBtn.addClass("disabled");
            resetBtn.addClass("disabled");
        }
        else{
            editBtn.removeClass("disabled");
            resetBtn.removeClass("disabled");
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

function PermissionFormatter(value, row, index){
    if(value===PERMS_SUBMITTER){
        return("Submitter");
    }
    else if(value===PERMS_MANAGER){
        return("Submitter");
    }
    else if(row.is_superuser){
        return('Super User');
    }
    else{
        return("View Only");
    }
}
//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/accounts/api/getaccounts",
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