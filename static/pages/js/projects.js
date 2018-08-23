var rowIDSelected = null;
$(document).ready(

    ////////////////////////////////////////////
    // Decleare project table
    //
    $(function () {
        $("#projectstable").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    title: "Project Name",
                    field: "name",
                    align: "center",
                    valign: "middle",
                    formatter: HrefFormater,
                    sortable: true
                },
                {
                    title: "Create Date",
                    field: "createDate",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    sortable: true
                },
                {
                    title: "Update Date",
                    field: "updateDate",
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
            url: "/projects/api/getprojects",
            method: "get",
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
    // Edit project
    //
    $("#editProjectPostForm").submit(function(e){
        var data = $('#editProjectPostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updateproject", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                var errStr = "Error: "+data.message;
                if(typeof data.detail.name !='undefined'){
                    errStr = errStr + ". Name: " + data.detail.name[0];
                }
                if(typeof data.detail.id !='undefined'){
                    errStr = errStr + ". ID: " + data.detail.id[0];
                }
                notification.html(errStr);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("The project is updated.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
            $("#projectstable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editProjectModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").hide();
    }),

    //////////////////////////////////////////
    // Add New project
    //
    $("#addProjectPostForm").submit(function(e){
        $.post("./api/addproject", $(this).serialize(), function(data){
            var notification = $("#retMsgAdd");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            // var closebtn = '<button type="button" class="close">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                var errStr = "Error: "+data.message;
                if(typeof data.detail.name !='undefined'){
                errStr = errStr + ". Name: " + data.detail.name[0] +'.';
                }
                if(typeof data.detail.id !='undefined'){
                    errStr = errStr + ". ID: " + data.detail.id[0] +'.';
                }
                notification.html(errStr);
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            if(data.notification != null){
                notification.html(data.notification);
            }
            else{
                notification.html("New project is added.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
            $("#projectstable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#addProjectModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //////////////////////////////////////////
    // Delete scan tasks
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains vuln ids
        var dataTable = $("#projectstable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deleteproject', $.param(data),
             function(returnedData){
                if(returnedData.status == 0){
                    $('#warningOnDelete').modal('hide');
                    $("#projectstable").bootstrapTable('refresh');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //////////////////////////////////////////
    // When the close does. Hide it instead of remove it with Dom
    //
    $('.alert').on('close.bs.alert', function (e) {
        $(this).addClass("hidden");
        e.preventDefault();
    }),

    //////////////////////////////////////////
    // show delete scan tasks warning
    //
    $("#delete").click(function () {
        var data = $("#projectstable").bootstrapTable('getSelections');
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
        var data = $("#projectstable").bootstrapTable('getSelections');
        if(data.length > 1){
            $('#msgInfo').text("Please choose only one row for editing.");
            $('#infoModal').modal('show');
        }
        else if (data.length == 1) {
            $('#id_name_edit').val(data[0].name);
            $('#id_description_edit').val(data[0].description);
            $('#editProjectModal').modal('show');
            rowIDSelected = data[0].id;
        }
    }),

    //////////////////////////////////////////
    // Detect changes on Select row to enable or disable Delete/ Edit button
    //
    $("#projectstable").change(function () {
        var data = $("#projectstable").bootstrapTable('getSelections');
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
    })
);

//////////////////////////////////////////
// Format href for bootstrap table
//
function HrefFormater(value, row, index) {
    return '<a href="' + row.id + '"> ' + row.name +'</a>';
}

//////////////////////////////////////////
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
