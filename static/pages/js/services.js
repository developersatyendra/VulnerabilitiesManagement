var rowIDSelected = null;
$(document).ready(

    //
    // Declear serivces table
    //
    $(function () {
        $("#servicetable").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    title: "Service Name",
                    field: "name",
                    align: "center",
                    valign: "middle",
                    formatter: HrefFormater,
                    sortable: true
                },
                {
                    title: "Port",
                    field: "port",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Date Added",
                    field: "dateCreated",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
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
            // url: "/services/api/getservices",
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
    // Edit service
    //,
    $("#editServicePostForm").submit(function(e){
        var data = $('#editServicePostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updateservice", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                notification.html("Error: "+data.message + '. '+data.detail.__all__[0]);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("The service is edited.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");

                // Disable Save button
                $("#saveEditBtn").attr('disabled', true);
            }
            notification.append(closebtn);
            $("#servicetable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editServiceModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //
    // Add New Service
    //
    $("#addServicePostForm").submit(function(e){
        $.post("./api/addservice", $(this).serialize(), function(data){
            var notification = $("#retMsgAdd");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                notification.html("Error: "+data.message + '. '+data.detail.__all__[0]);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("New service is added.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");

                // Disable Save button
                $("#saveAddBtn").attr('disabled', true);
            }
            notification.append(closebtn);
            $("#servicetable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#addServiceModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete service
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains service ids
        var dataTable = $("#servicetable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deleteservice', $.param(data),
             function(returnedData){
                if(returnedData.status == 0){
                    $('#warningOnDelete').modal('hide');
                    $("#servicetable").bootstrapTable('refresh');

                    $('#msgInfo').text(returnedData.message);
                    $('#infoModal').modal('show');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete service warning
    //
    $("#delete").click(function () {
        var data = $("#servicetable").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected service?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected services?");
            }
            $('#warningOnDelete').modal('show')
        }
    }),
    //
    // Fill in edit form when edit btn is clicked
    //
    $("#edit").click(function () {
        var data = $("#servicetable").bootstrapTable('getSelections');
        if(data.length > 1){
            $('#msgInfo').text("Please choose only one row for editing.");
            $('#infoModal').modal('show');
        }
        else if (data.length == 1) {
            $('#id_name_edit').val(data[0].name);
            $('#id_port_edit').val(data[0].port);
            $('#id_description_edit').val(data[0].description);
            $('#editServiceModal').modal('show');
            rowIDSelected = data[0].id;

            // Dissable Save Edit Button
            $("#saveEditBtn").attr('disabled', true);
        }
    }),
    //
    // Check how many row is selected to enable or disable edit and delete button
    //
    $("#servicetable").change(function () {
        var data = $("#servicetable").bootstrapTable('getSelections');
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
    $('#addServicePostForm').change(function () {
        $('#saveAddBtn').attr('disabled', false);
    }),
    $("#id_name").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_port").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),

    // Edit form
    $('#editServicePostForm').change(function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_name_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_port_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_description_edit").on("input", function () {
        $("#saveEditBtn").attr('disabled', false);
    })
);

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

// Format Href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="' + row.id + '"> ' + row.name +'</a>';
}

//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/services/api/getservices",
        data: params.data,
        dataType: "json",
        success: function (data) {
            if (data.status == 0) {
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