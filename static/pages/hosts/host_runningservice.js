var rowIDSelected = null;
var url = window.location.pathname;
var id = url.split("/")[2];
$(document).ready(
    getHostName(),
    //
    // Declear serivces table
    //
    $(function () {
        $("#hostRunningService").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    checkbox: true,
                    width: '3%',
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
            showExport: true,
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
    // Enable save button
    $('#id_service').change(function () {
       $('#saveAddBtn').attr('disabled', false);
    }),

    // Add running serivce
    $("#addRunningSerivceForm").submit(function(e){
        var data = $(this).serializeArray();
        data.push({name: "id", value: id});
        data = $.param(data);
        $.post("/hosts/api/addrunningservice", data, function(data){
            var notification = $("#retMsgAdd");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.status != 0){
                notification.html("Error: "+data.message + '.');
                notification.removeClass("alert-info");
                notification.addClass("alert-danger");
            }
            else{
                notification.html("The new running serivce is added.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");

                // Disable Save Edit Button
                $('#saveAddBtn').attr('disabled', true);
            }
            notification.append(closebtn);
            $("#hostRunningService").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#addRunningServiceModel").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete Running Service
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains Host ids
        var dataTable = $("#hostRunningService").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "services", value: ids});
        data.push({name: "id", value: id});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('/hosts/api/removerunningservice', $.param(data),
             function(returnedData){
                if(returnedData.status == 0){
                    $('#warningOnDeleteModal').modal('hide');
                    $("#hostRunningService").bootstrapTable('refresh');

                    $('#msgInfo').text(returnedData.message);
                    $('#infoModal').modal('show');
                }
        }, 'json');
        $('#warningOnDeleteModal').modal('hide')
    }),

    //////////////////////////////////////////
    // When the close does. Hide it instead of remove it with Dom
    //
    $('.alert').on('close.bs.alert', function (e) {
        $(this).addClass("hidden");
        e.preventDefault();
    }),

    //
    // Check how many row is selected to enable or disable edit and delete button
    //
    $("#hostRunningService").change(function () {
        var data = $("#hostRunningService").bootstrapTable('getSelections');
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

    // show delete warning
    $("#delete").click(function () {
        var data = $("#hostRunningService").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected running service?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected running services?");
            }
            $('#warningOnDeleteModal').modal('show')
        }
    }),
);

// Format href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="' + '/services/' +row.id + '"> ' + row.name +'</a>';
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

//////////////////////////////////////////
// Custom params for bootstrap table
//
function queryParams(params) {
    // params.advFilter = "projectID";
    params.hostID = id;
    return(params);
    // return {advFilter: 'projectID', advFilterValue: id};
}


//////////////////////////////////////////
// Custom params for bootstrap table
//
function getHostName(){
     $.ajax({
         type: "GET",
         url: "/hosts/api/gethostname",
         data: {id: id},
         dataType: "json",
         success: function (data) {
             if (data.status == 0) {
                 $('#brHost').text(data.object)
             }
         },
     })
}