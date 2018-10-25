var rowIDSelected = null;
var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -2];
$(document).ready(
    //////////////////////////////////////////
    // Decleare scan tasks table
    //
    $(function () {
        $("#scanhoststable").bootstrapTable({
            columns: [
                {
                    title: "Hostname",
                    field: "hostName",
                    align: "center",
                    valign: "middle",
                    formatter: HostHrefFormater,
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
                    title: "Start Time",
                    field: "startTime",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    sortable: true
                },
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
                },
            ],
            showExport: true,
            ajax: ajaxRequest,
            detailView: true,
            queryParamsType: "",
            idField: "id",
            striped: true,
            pagination: true,
            sidePagination: "server",
            pageList: [5, 10, 20, 50, 100, 200, 'All'],
            search: true,
            onExpandRow: function (index, row, $detail) {
                $detail.html('<table></table>').find('table').bootstrapTable({
                    columns: [{
                        title: "Vulnerability",
                        width: '27%',
                        field: "name",
                        align: "center",
                        valign: "middle",
                        formatter: function (value, row, index) {
                            return '<a href="/vuln/' + row.id + '"> ' + row.name +'</a>';
                        },
                        sortable: true
                    },
                        {
                            title: "Level Risk",
                            width: '5%',
                            field: "levelRisk",
                            align: "center",
                            valign: "middle",
                            sortable: true
                        },
                        {
                            title: "CVE",
                            width: '10%',
                            field: "cve",
                            align: "center",
                            valign: "middle",
                            sortable: true
                        },
                        {
                            title: "Service",
                            width: '10%',
                            field: "service.name",
                            align: "center",
                            valign: "middle",
                            sortable: true
                        }],
                    ajax: function ajaxRequest(params) {
                        $.ajax({
                            type: "GET",
                            url: "/vuln/api/getvulns",
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
                    },
                    idField: "id",
                    queryParams: function (params) {
                        params.scanID = id;
                        params.hostID = row.id;
                        return (params);
                    },
                    queryParamsType: "",
                    striped: true,
                    pagination: true,
                    sidePagination: "server",
                    pageList: [5, 10, 20, 50, 100, 200, 'All'],
                    search: false,
                })
            }
        })
    }),


    //////////////////////////////////////////
    // Fill scan name to br
    //

    GetScanName(),
);

// Format href for bootstrap table
function HostHrefFormater(value, row, index) {
    return '<a href="/hosts/' + row.id + '"> ' + row.hostName +'</a>';
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
    var urlGetData = "/hosts/api/gethostsvuln?scanID="+id;
    $.ajax({
        type: "GET",
        url: urlGetData,
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
// Get ScanName
//
function GetScanName(){
     $.ajax({
         type: "GET",
         url: "/scans/api/getscanname",
         data: {id: id},
         dataType: "json",
         success: function (data) {
             if (data.status == 0) {
                 $('#brScan').text(data.object)
             }
         },
     })
}