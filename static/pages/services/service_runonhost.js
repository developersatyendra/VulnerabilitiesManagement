var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -2];
var rowIDSelected = null;
$(document).ready(
    //
    // Decleare vulnerability table
    //
    $(function () {
        $("#runonhosttable").bootstrapTable({
            columns:[
                {
                    title: "Hostname",
                    width: '20%',
                    field: "hostName",
                    align: "center",
                    formatter: HrefFormater,
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "IP Address",
                    width: '15%',
                    field: "ipAddr",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "OS Name",
                    width: '30%',
                    field: "osName",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Description",
                    width: '42%',
                    field: "description",
                    align: "center",
                    valign: "middle",
                    sortable: true
                }
            ],
            // url: "/vuln/api/getvulns",
            // method: "get",
            ajax: ajaxRequest,
            idField: "id",
            queryParams: queryParams,
            queryParamsType: "",
            striped: true,
            pagination: true,
            sidePagination: "server",
            pageList: [5, 10, 20, 50, 100, 200, 'All'],
            search: true,
        })
    }),


    //
    // Edit vuln
    //
    $("#editVulnPostForm").submit(function(e){
        var data = $('#editVulnPostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updatevuln", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                notification.html("Error: "+data.message + '. '+data.detail.name[0]);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("The vulnerability is edited.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");

                // Disable Save button
                $("#saveEditBtn").attr('disabled', true);
            }
            notification.append(closebtn);
            $("#vulntable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editVulnModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //
    // Add New vuln
    //
    $("#addVulnPostForm").submit(function(e){
        $.post("./api/addvuln", $(this).serialize(), function(data){
            var notification = $("#retMsgAdd");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                notification.html("Error: "+data.message + '. '+data.detail.name[0]);
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
            $("#vulntable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#addVulnModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete vuln
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains vuln ids
        var dataTable = $("#vulntable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deletevuln', $.param(data),
             function(returnedData){
                if(returnedData.status == 0){
                    $('#warningOnDelete').modal('hide');
                    $("#vulntable").bootstrapTable('refresh');

                    $('#msgInfo').text(returnedData.message);
                    $('#infoModal').modal('show');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete vuln warning
    //
    $("#delete").click(function () {
        var data = $("#vulntable").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected vulnerability?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected vulnerabilities?");
            }
            $('#warningOnDelete').modal('show')
        }
    }),
    //
    // Fill in edit form when edit btn is clicked
    //
    $("#edit").click(function () {
        var data = $("#vulntable").bootstrapTable('getSelections');
        if(data.length > 1){
            $('#msgInfo').text("Please choose only one row for editing.");
            $('#infoModal').modal('show');
        }
        else if (data.length == 1) {
            $('#id_name_edit').val(data[0].name);
            $('#id_levelRisk_edit').val(data[0].levelRisk);
            $('#id_cve_edit').val(data[0].cve);
            $('#id_service_edit').val(data[0].service.id);
            $('#id_observation_edit').val(data[0].observation);
            $('#id_recommendation_edit').val(data[0].recommendation);
            $('#id_description_edit').val(data[0].description);
            $('#editVulnModal').modal('show');
            rowIDSelected = data[0].id;

            // Disable Save Edit
            $("#saveEditBtn").attr('disabled', true);
        }
    }),

    $("#vulntable").change(function () {
        var data = $("#vulntable").bootstrapTable('getSelections');
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
    $('#addVulnPostForm').change(function () {
        $('#saveAddBtn').attr('disabled', false);
    }),
    $("#id_name").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_levelRisk").on("input", function(){
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_cve").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_observation").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_recommendation").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),
    $("#id_description").on("input", function () {
        $("#saveAddBtn").attr('disabled', false);
    }),

    // Edit form
    $('#editVulnPostForm').change(function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_name_edit").on("input", function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_levelRisk_edit").on("input", function(){
        $("#saveEditBtn").attr('disabled', false);
    }),
    $("#id_cve_edit").on("input", function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_observation_edit").on("input", function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_recommendation_edit").on("input", function () {
        $('#saveEditBtn').attr('disabled', false);
    }),
    $("#id_description_edit").on("input", function () {
        $('#saveEditBtn').attr('disabled', false);
    })
);

// Format Href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="/hosts/' + row.id + '"> ' + row.hostName +'</a>';
}

//////////////////////////////////////////
// Custom params for bootstrap table
//
function queryParams(params) {
    // params.advFilter = "projectID";
    params.serviceID = id;
    return(params);
    // return {advFilter: 'projectID', advFilterValue: id};
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