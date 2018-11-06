var rowIDSelected = null;
var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -2];
var __vulnTop = 10;
$(document).ready(
    // Draw Charts
    DrawChartScanResult(),
    DrawChartServiceStat(),


    // Fill Br by Scan Name
    GetScanName(),
    //////////////////////////////////////////
    // Decleare vulns table
    //
    $(function () {
        $("#vulntable").bootstrapTable({
            columns:[
                {
                    title: "Vulnerability",
                    width: '90%',
                    field: "name",
                    align: "center",
                    valign: "middle",
                    formatter: HrefFormater,
                    sortable: false
                },
                {
                    title: "Risk",
                    width: '10%',
                    field: "levelRisk",
                    align: "center",
                    valign: "middle",
                    sortable: false
                }
                // {
                //     title: "CVE",
                //     width: '10%',
                //     field: "cve",
                //     align: "center",
                //     valign: "middle",
                //     sortable: true
                // }
            ],
            pagination: true,
            pageSize: 5,
            pageList: [5],//, 10, 20, 50, 100, 200, 'All'],
            search: false,
            ajax: ajaxRequest,
            queryParams: queryParams,
            idField: "id",
            queryParamsType: "",
            striped: true,
            sidePagination: "server",
            // formatRecordsPerPage: function () {
            //     return ''
            // },
            // formatShowingRows: function () {
            //     return ''
            // }
        })
    }),
    // Top vuln DropDown Button
    $(".choice li a").click(function(event){
        $(this).parents(".dropdown").find('.btn').html('<i class="fa fa-angle-double-up fa-fw"></i>' + $(this).text() + ' <span class="caret"></span>');
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
        __vulnTop = parseInt($(this).attr('id'));
        $("#vulntable").bootstrapTable('refresh');
        event.preventDefault();
    }),
);

// Get Br
function GetScanName(){
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

// Format Href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="/vuln/' + row.id + '"> ' + row.name +'</a>';
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
function queryParams(params) {
    params.hostID = id;
    params.pageSize =5;
    params.sortOrder = 'desc';
    return(params);
}
//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/vuln/api/getcurrenthostvuln",
        data: params.data,
        dataType: "json",
        success: function(data) {
            if(data.status == 0){
                params.success({
                    "rows": data.object.rows,
                    "total": __vulnTop
                })
            }
        },
       error: function (er) {
            params.error(er);
        }
    });
}


//////////////////////////////////////////
// Draw Chart
function DrawChartScanResult(){
    function GetData() {
        return $.ajax({
            url:'/scans/api/getscansvulns?hostID='+id,
            success: function (data) {
                if(data.status ==0)
                    rawData = data.rows;
            }
        });
    }
    $.when(GetData()).done(function (results){
        if(results.status <0)
            return -1;
        var rawData = results.object.rows;
        var labels = [];
        var dataset_high = [];
        var dataset_med = [];
        var dataset_low = [];
        var dataset_info = [];
        for(i=0; i<rawData.length;i++){
            labels.push(rawData[i].name);
            dataset_high.push(rawData[i].high);
            dataset_med.push(rawData[i].med);
            dataset_low.push(rawData[i].low);
            dataset_info.push(rawData[i].info);
        }
        var ctx = document.getElementById("scanOverViewChart").getContext("2d");
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Information',
                        data: dataset_info,
                        backgroundColor: '#4B98FF' // blue
                    },
                    {
                        label: 'Low',
                        data: dataset_low,
                        backgroundColor: '#F2B705' // yellow
                    },
                    {
                        label: 'Medium',
                        data: dataset_med,
                        backgroundColor: '#df7416' // orange
                    },
                    {
                        label: 'High',
                        data: dataset_high,
                        backgroundColor: '#bf0404' // red
                    }
                    ]
            },
            options: {
                legend: {display: false},
                title: {
                    display: true,
                    text: 'Scan Result'
                },
                scales: {
                    xAxes: [{ stacked: true }],
                    yAxes: [{ stacked: true }]
                }
            }
        });
    })
}


function DrawChartServiceStat(){
    function GetData() {
        return $.ajax({
            url:'/services/api/getservicesvuln?sortName=total&hostID='+id,
            method: "GET",
            success: function (data) {
                if(data.status ==0)
                    rawData = data.object;
            }
        });
    }
    $.when(GetData()).done(function (results){
        if(results.status <0)
            return -1;
        var rawData = results.object.rows;
        var labels = [];
        var dataset = [];
        for(i=0; i<rawData.length;i++){
            labels.push(rawData[i].name + ' - '+rawData[i].port);
            dataset.push(rawData[i].total);
        }

        var ctx = document.getElementById("vulnStatBySrv").getContext("2d");
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels ,
                datasets: [
                    {
                        data: dataset,
                        backgroundColor: '#4B98FF'
                    }]
            },
            options: {
                legend: {display: false},
                responsive: true,
                title: {
                    display: true,
                    text: 'Statistics of vulnerabilities by services'
                }
            }
        });
    })
}