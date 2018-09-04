var rowIDSelected = null;
$(document).ready(

    //
    // Declear serivces table
    //
    $(function () {
        $("#hosttable").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    title: "Hostname",
                    field: "hostName",
                    align: "center",
                    formatter: HrefFormater,
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "IP Address",
                    field: "ipAddr",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "OS Name",
                    field: "osName",
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
            // url: "/hosts/api/gethosts",
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

    //
    // Edit host
    //
    $("#editHostPostForm").submit(function(e){
        var data = $('#editHostPostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updatehost", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                notification.html("Error: "+data.message + '. '+data.detail.ipAddr[0]);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("The host is edited.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");

                // Disable Save Edit Button
                $('#saveEditBtn').attr('disabled', true);
            }
            notification.append(closebtn);
            $("#hosttable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editHostModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //
    // Add New Service
    //
    $("#addHostPostForm").submit(function(e){
        $.post("./api/addhost", $(this).serialize(), function(data){
            var notification = $("#retMsgAdd");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                notification.html("Error: "+data.message + '. '+data.detail.ipAddr[0]);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("New Host is added.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");

                // Disable Save Add button
                $('#saveAddBtn').attr('disabled', true);
            }
            notification.append(closebtn);
            $("#hosttable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#addHostModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete Host
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains Host ids
        var dataTable = $("#hosttable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deletehost', $.param(data),
             function(returnedData){
                if(returnedData.status == 0){
                    $('#warningOnDelete').modal('hide');
                    $("#hosttable").bootstrapTable('refresh');

                    $('#msgInfo').text(returnedData.message);
                    $('#infoModal').modal('show');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete Host warning
    //
    $("#delete").click(function () {
        var data = $("#hosttable").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected Host?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected Hosts?");
            }
            $('#warningOnDelete').modal('show')
        }
    }),

        //
    // Fill in edit form when edit btn is clicked
    //
    $("#edit").click(function () {
        var data = $("#hosttable").bootstrapTable('getSelections');
        if (data.length == 1) {
            $('#id_hostName_edit').val(data[0].hostName);
            $('#id_ipAddr_edit').val(data[0].ipAddr);
            $('#id_osName_edit').val(data[0].osName);
            $('#id_osVersion_edit').val(data[0].osVersion);
            $('#id_description_edit').val(data[0].description);
            $('#editHostModal').modal('show');
            rowIDSelected = data[0].id;

            // Disable Save Edit Button
            $('#saveEditBtn').attr('disabled', true);
        }
    }),
    //
    // Check how many row is selected to enable or disable edit and delete button
    //
    $("#hosttable").change(function () {
        var data = $("#hosttable").bootstrapTable('getSelections');
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
    $('#addHostPostForm').change(function () {
        $('#saveAddBtn').attr('disabled', false);
    }),
    $("#id_hostName").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_ipAddr").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_osName").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_osVersion").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),

    // Edit form
    $('#editHostModal').change(function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_hostName_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_ipAddr_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_osName_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_osVersion_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_description_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    })

);

// Format Href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="./' + row.id + '"> ' + row.hostName +'</a>';
}

//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/hosts/api/gethosts",
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