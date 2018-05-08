
var data= [
    {
        "id": "2",
        "serviceName": "HTTP",
        "port": "80",
        "description": "World Wide Web Protocol"
    },
    {
        "id": "2",
        "serviceName": "HTTP",
        "port": "80",
        "description": "World Wide Web Protocol"
    },
    {
        "id": "2",
        "serviceName": "HTTP",
        "port": "80",
        "description": "World Wide Web Protocol"
    },
    {
        "id": "2",
        "serviceName": "HTTP",
        "port": "80",
        "description": "World Wide Web Protocol"
    },
    {
        "id": "2",
        "serviceName": "HTTP",
        "port": "80",
        "description": "World Wide Web Protocol"
    },
    {
        "id": "2",
        "serviceName": "HTTP",
        "port": "80",
        "description": "World Wide Web Protocol"
    },
    {
        "id": "2",
        "serviceName": "HTTP",
        "port": "80",
        "description": "World Wide Web Protocol"
    },
    {
        "id": "1",
        "serviceName": "HTTPS",
        "port": "443",
        "description": "HTTP secure"
    },
    {
        "id": "1",
        "serviceName": "HTTPS",
        "port": "443",
        "description": "HTTP secure"
    },
    {
        "id": "1",
        "serviceName": "HTTPS",
        "port": "443",
        "description": "HTTP secure"
    },
    {
        "id": "1",
        "serviceName": "HTTPS",
        "port": "443",
        "description": "HTTP secure"
    },
    {
        "id": "1",
        "serviceName": "HTTPS",
        "port": "443",
        "description": "HTTP secure"
    },
    {
        "id": "1",
        "serviceName": "HTTPS",
        "port": "443",
        "description": "HTTP secure"
    }
];
$(document).ready(

    $(function () {
        $("#servicetable").bootstrapTable({
            columns:[
                {
                  field: 'state',
                  checkbox: true,
                  align: 'center',
                  valign: 'middle'
                },
                {
                  title: "ID",
                  field: "id",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Service Name",
                  field: "serviceName",
                  align: "center",
                  valign: "middle",
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
                  title: "Description",
                  field: "description",
                  align: "center",
                  valign: "middle",
                  sortable: true
                }
            ],
            url: "/services/api/getservices",
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
    $("#AddServicePostForm").submit(function(e){
        $.post("./api/addservice", $(this).serialize(), function(data){
            var notification = $("#AfterPostMess");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.notification != null){
                notification.html(data.notification);
            }
            else{
                notification.html("New service is added.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
        });
        e.preventDefault();
    }),
    $("#addServiceModal").on("hidden.bs.modal", function () {
        $("#servicetable").bootstrapTable('refresh');
    })
);

