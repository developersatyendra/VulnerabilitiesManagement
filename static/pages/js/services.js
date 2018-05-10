
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
                  field: "name",
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
        $("#AfterPostMess").addClass("hidden");
        $("#servicetable").bootstrapTable('refresh');
    }),
    // $("#delete").click(function () {
    //     var data = JSON.stringify($("#servicetable").bootstrapTable('getSelections'));
    //     $.ajax({
    //             type: "POST",
    //             url: "./api/deleteservice",
    //             data: {
    //              data: data,
    //              csrfmiddlewaretoken: '{{ csrf_token }}'
    //             },
    //             contentType: "application/json; charset=utf-8",
    //             async: false,
    //             dataType: 'json',
    //             success: function(msg) {
    //              $("#servicetable").bootstrapTable('refresh');
    //              alert(msg.retVal);
    //             }
    //     });
    // })
    // $("#confirmDelete").click(function () {
    //     var data = JSON.stringify($("#servicetable").bootstrapTable('getSelections'));
    //     $.ajax({
    //          type: "POST",
    //          url: "./api/deleteservice",
    //          data: data,
    //          contentType: "application/json; charset=utf-8",
    //          dataType: "json",
    //          success: function(msg) {
    //              $("#servicetable").bootstrapTable('refresh');
    //              alert(msg.retVal);
    //          }
    //     });
    //     $('#warningOnDelete').modal('hide')
    // }),
    // $("#delete").click(function () {
    //     var data = $("#servicetable").bootstrapTable('getSelections');
    //     if(data.length > 0){
    //         $('#warningOnDelete').modal('show')
    //     }
    // })

);

