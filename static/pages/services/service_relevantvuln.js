var url = window.location.pathname;
var id = url.split("/")[url.split("/").length -2];
var rowIDSelected = null;
$(document).ready(
    //
    // Decleare vulnerability table
    //
    $(function () {
        $("#relevantvulntable").bootstrapTable({
            columns:[
                {
                    title: "Vulnerability",
                    width: '27%',
                    field: "name",
                    align: "center",
                    valign: "middle",
                    formatter: HrefFormater,
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
                },
                {
                    title: "Description",
                    width: '45%',
                    field: "description",
                    align: "center",
                    valign: "middle",
                    sortable: true
                }
            ],
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
    GetServiceName()
);

// Format Href for bootstrap table
function HrefFormater(value, row, index) {
    return '<a href="/vuln/' + row.id + '"> ' + row.name +'</a>';
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
        url: "/vuln/api/getvulns",
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
// Get Service name
//
function GetServiceName(){
     $.ajax({
         type: "GET",
         url: "/services/api/getservicename",
         data: {id: id},
         dataType: "json",
         success: function (data) {
             if (data.status == 0) {
                 $('#brService').text(data.object)
             }
         },
     })
}