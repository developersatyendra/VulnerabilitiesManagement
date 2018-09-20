var rowIDSelected = null;
var url = window.location.pathname;
var id = url.split("/")[2];
$(document).ready(
    //
    // Decleare vulnerability table
    //
    $(function () {
        $("#vulnHostInvoledtable").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    width: '3%',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    title: "Hostname",
                    width: '30%',
                    field: "hostName",
                    align: "center",
                    formatter: HostHrefFormater,
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
                    title: "Scan Name",
                    width: '30%',
                    field: "scanName",
                    align: "center",
                    formatter: ScanHrefFormater,
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Start Time",
                    width: '22%',
                    field: "startTime",
                    align: "center",
                    formatter: FormattedDate,
                    valign: "middle",
                    sortable: true
                }
            ],
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
    //////////////////////////////////////////
    // Fill name vuln in br
    //
    getVulnName()
);

// Format Href for bootstrap table
function HostHrefFormater(value, row, index) {
    return '<a href="/hosts/' + row.id + '"> ' + row.hostName +'</a>';
}

function ScanHrefFormater(value, row, index) {
    return '<a href="/scans/' + row.idScan + '"> ' + row.scanName +'</a>';
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
// Custom params for bootstrap table
//
function queryParams(params) {
    // params.advFilter = "projectID";
    params.vulnID = id;
    return(params);
    // return {advFilter: 'projectID', advFilterValue: id};
}

//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/hosts/api/gethostsvuln",
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
function getVulnName() {
    $.ajax({
        type: "GET",
        url: "/vuln/api/getvulnname",
        data: {id: id},
        dataType: "json",
        success: function (data) {
            if (data.status == 0) {
                $('#brVuln').text(data.object)
            }
        },
    })
}