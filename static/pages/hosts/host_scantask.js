var rowIDSelected = null;
var url = window.location.pathname;
var id = url.split("/")[2];
$(document).ready(

    //
    // Declear serivces table
    //
    $(function () {
        $("#hostScanTask").bootstrapTable({
            columns:[[
                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle',
                    rowspan: 2
                },
                {
                    title: "Scan Task",
                    field: "name",
                    align: "center",
                    valign: "middle",
                    formatter: HrefFormater,
                    rowspan: 2,
                    sortable: true
                },
                {
                    title: "Start Time",
                    field: "startTime",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    rowspan: 2,
                    sortable: true
                },
                {
                    title: "Finished Time",
                    field: "endTime",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    rowspan: 2,
                    sortable: true
                },
                {
                    title: "Processed",
                    field: "isProcessed",
                    align: "center",
                    valign: "middle",
                    formatter: BooleanFormatter,
                    rowspan: 2,
                    sortable: true
                },
                {
                    title: "Host Vulnerabilities",
                    align: "center",
                    valign: "middle",
                    colspan: 4
                }],[
                {
                    title: "High",
                    field: "high",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Medium",
                    field: "med",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Low",
                    field: "low",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Information",
                    field: "info",
                    align: "center",
                    valign: "middle",
                    sortable: true
                }
            ]],
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
    getHostName()
);

// Format href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="' + '/scans/' +row.id + '"> ' + row.name +'</a>';
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
        url: "/scans/api/getscansvulns",
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