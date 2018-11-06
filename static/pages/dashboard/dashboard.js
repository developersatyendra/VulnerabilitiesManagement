var rowIDSelected = null;
var url = window.location.pathname;
var __vulnTop = 10;
var __hostTop = 10;
$(document).ready(
    // Draw Charts
    DrawChartProjectVuln(),
    DrawChartOSStat(),
    DrawChartServiceStat(),
    DrawChartRecentScan(),

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
        })
    }),
    $(function () {
        $("#hosttable").bootstrapTable({
            columns:[
                {
                    title: "Hostname",
                    width: '60%',
                    field: "name",
                    align: "center",
                    valign: "middle",
                    formatter: HrefHostFormater,
                    sortable: false
                },
                {
                    title: "High",
                    width: '10%',
                    field: "high",
                    align: "center",
                    valign: "middle",
                    sortable: false
                },
                {
                    title: "Med",
                    width: '10%',
                    field: "med",
                    align: "center",
                    valign: "middle",
                    sortable: false
                },
                {
                    title: "Low",
                    width: '10%',
                    field: "low",
                    align: "center",
                    valign: "middle",
                    sortable: false
                },
                {
                    title: "Info",
                    width: '10%',
                    field: "info",
                    align: "center",
                    valign: "middle",
                    sortable: false
                }
            ],
            pagination: true,
            pageSize: 5,
            pageList: [5],//, 10, 20, 50, 100, 200, 'All'],
            search: false,
            ajax: ajaxHostRequest,
            queryParams: queryParams,
            idField: "id",
            queryParamsType: "",
            striped: true,
            sidePagination: "server",
        })
    }),
    // Top vuln DropDown Button
    $(".vulntop li a").click(function(event){
        $(this).parents(".dropdown").find('.btn').html('<i class="fa fa-angle-double-up fa-fw"></i>' + $(this).text() + ' <span class="caret"></span>');
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
        __vulnTop = parseInt($(this).attr('id'));
        $("#vulntable").bootstrapTable('refresh');
        event.preventDefault();
    }),
    $(".hosttop li a").click(function(event){
        $(this).parents(".dropdown").find('.btn').html('<i class="fa fa-angle-double-up fa-fw"></i>' + $(this).text() + ' <span class="caret"></span>');
        $(this).parents(".dropdown").find('.btn').val($(this).data('value'));
        __hostTop = parseInt($(this).attr('id'));
        $("#hosttable").bootstrapTable('refresh');
        event.preventDefault();
    }),
);


// Format Href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="/vuln/' + row.id + '"> ' + row.name +'</a>';
}
function HrefHostFormater(value, row, index) {
    return '<a href="/hosts/' + row.id + '"> ' + row.hostName + '<br>' +row.ipAddr +'</a>';
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
    params.pageSize =5;
    params.sortOrder='desc';
    return(params);
}
//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/vuln/api/getcurrentglobalvuln",
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

function ajaxHostRequest(params) {
    $.ajax({
        type: "GET",
        url: "/hosts/api/gethostscurrentvuln",
        data: params.data,
        dataType: "json",
        success: function(data) {
            if(data.status == 0){
                params.success({
                    "rows": data.object.rows,
                    "total": __hostTop
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
function DrawChartProjectVuln(){
    function GetData() {
        return $.ajax({
            url:'/projects/api/getprojectvulns',
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
        var dataset_numScanTasks = [];
        var sumHigh = 0;
        var sumMed = 0;
        var sumLow = 0;
        var sumInfo = 0;

        for(i=0; i<rawData.length;i++){
            sumHigh += rawData[i].high;
            sumMed += rawData[i].med;
            sumLow += rawData[i].low;
            sumInfo += rawData[i].info;
            labels.push(rawData[i].name);
            dataset_high.push(rawData[i].high);
            dataset_med.push(rawData[i].med);
            dataset_low.push(rawData[i].low);
            dataset_info.push(rawData[i].info);
            dataset_numScanTasks.push(rawData[i].numScanTasks);
        }
        $('#panel-high').text(sumHigh);
        $('#panel-med').text(sumMed);
        $('#panel-low').text(sumLow);
        $('#panel-info').text(sumInfo);

        var ctx = document.getElementById("chartProjectNum").getContext("2d");
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Scan Task',
                        data: dataset_numScanTasks,
                        // backgroundColor: '#bf0404' // red,
                        borderColor: '#72767A', // gray
                        yAxisID: 'rightY',
                        type: 'line',
                        fill: false,
                    },
                    {
                        label: 'Information',
                        data: dataset_info,
                        yAxisID: 'leftY',
                        backgroundColor: '#4B98FF' // blue
                    },
                    {
                        label: 'Low',
                        data: dataset_low,
                        yAxisID: 'leftY',
                        backgroundColor: '#F2B705' // yellow
                    },
                    {
                        label: 'Medium',
                        data: dataset_med,
                        yAxisID: 'leftY',
                        backgroundColor: '#df7416' // orange
                    },
                    {
                        label: 'High',
                        data: dataset_high,
                        yAxisID: 'leftY',
                        backgroundColor: '#bf0404' // red
                    }
                ]
            },
            options: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'Project Overview'
                },
                scales: {
                    xAxes: [
                        {
                            stacked: true
                        }
                    ],
                    yAxes: [
                        {
                            id: 'leftY',
                            // type: 'linear',
                            position: 'left',
                            stacked: true
                        },
                        {
                            id: 'rightY',
                            // type: 'linear',
                            position: 'right',
                            // stacked: true
                        }
                    ]
                }
            }
        });
    })
}

function DrawChartOSStat(){
    function GetData() {
        return $.ajax({
            url:'/hosts/api/gethostsos',
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
        var dataset = [0, 0, 0, 0, 0];
        for(i=0; i<rawData.length;i++){
            if(String(rawData[i].osType).toLowerCase() === 'windows')
                dataset[0] += 1;
            else if(String(rawData[i].osType).toLowerCase() === 'linux')
                dataset[1] += 1;
            else if(String(rawData[i].osType).toLowerCase() === 'unix')
                dataset[2] += 1;
            else if(String(rawData[i].osType).toLowerCase() === 'cisco ios')
                dataset[3] += 1;
            else
                dataset[4] += 1;
        }
        var labels = ['Windows', 'Linux', 'Unix', 'Cisco IOS', 'Others'];
        for(i=0; i<dataset.length; i++){
            if(dataset[i] === 0){
                labels.splice(i,1);
                dataset.splice(i,1);
                i--;
            }
        }
        var ctx = document.getElementById("osStatisticChart").getContext("2d");
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels ,
                datasets: [
                    {
                        data: dataset,
                        backgroundColor: ['#4B98FF', '#3F80D6', '#366EB8', '#2D5C99', '#28528A', '#24497A', '#214370', '#172F4F', '#12253D', '#0D1B2E', '#08111C', '#04090F', '#03060A']
                    }]
            },
            options: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                title: {
                    display: true,
                    text: 'OS Statistic'
                }
            }
        });
    })
}

function DrawChartServiceStat(){
    function GetData() {
        return $.ajax({
            url:'/services/api/getservicesvuln?sortName=total',
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

function DrawChartRecentScan(){
    function GetData() {
        return $.ajax({
            url:'/scans/api/getscansvulns?sortName=startTime&pageSize=15',
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
        var ctx = document.getElementById("recentScanningTask").getContext("2d");
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
                    text: 'Recent Scanning Tasks'
                },
                scales: {
                    xAxes: [{ stacked: true }],
                    yAxes: [{ stacked: true }]
                }
            }
        });
    })
}