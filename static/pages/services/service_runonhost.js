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