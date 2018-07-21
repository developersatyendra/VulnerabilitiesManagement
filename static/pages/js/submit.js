var rowIDSelected = null;
$(document).ready(
    //
    // Declear serivces table
    //
    $(function () {
        $("#submittable").bootstrapTable({
            columns:[
                {
                  field: 'state',
                  checkbox: true,
                  align: 'center',
                  valign: 'middle'
                },
                {
                  title: "File Name",
                  field: "fileSubmitted",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Date Submit",
                  field: "dateCreated",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Scan Task",
                  field: "scanTask.name",
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
            url: "/submit/api/getsubmits",
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

    //
    // Edit service
    //
    $('#servicetable').on('click-row.bs.table',function (e, row, element, field) {
        $('#id_name_edit').val(row.name);
        $('#id_port_edit').val(row.port);
        $('#id_description_edit').val(row.description);
        $('#editServiceModal').modal('show');
        rowIDSelected = row.id;
    }),
    $("#editServicePostForm").submit(function(e){
        var data = $('#editServicePostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updateservice", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.notification != null){
                notification.html(data.notification);
            }
            else{
                notification.html("The service is edited.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
            $("#submittable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editServiceModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //
    // Add New Service
    //
    $("#addSubmitPostForm").submit(function(e){
        var formData = new FormData(this);
        $.ajax({
            url: "./api/addsubmit",
            type: 'POST',
            data: formData,
            success: function (data) {
                var body = $("#retInfoBody");
                var title = $("#retInfoTitle");
                if(data.notification != null){
                    title.text("Error");
                    body.text(data.notification);
                }
                else{
                    title.text("Infomation");
                    body.text("File was submitted successfully")
                }
                $("#retInfoModal").modal('show');
                $("#servicetable").bootstrapTable('refresh');
            },
            cache: false,
            contentType: false,
            processData: false
        });
        e.preventDefault();
    //     $.post("./api/addsubmit", $(this).serialize(), function(data){
    //         var body = $("#retInfoBody");
    //         var title = $("#retInfoTitle");
    //         if(data.notification != null){
    //             title.text("Error");
    //             body.text(data.notification);
    //         }
    //         else{
    //             title.text("Infomation");
    //             body.text("File was submitted successfully")
    //         }
    //         $("#retInfoModal").modal('show');
    //         $("#servicetable").bootstrapTable('refresh');
    //     });
    //     e.preventDefault();
    // }),
    // $("#addServiceModal").on("hidden.bs.modal", function () {
    //     $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete service
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains service ids
        var dataTable = $("#servicetable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deleteservice', $.param(data),
             function(returnedData){
                if(returnedData.retVal > 0){
                    $('#warningOnDelete').modal('hide');
                    $("#servicetable").bootstrapTable('refresh');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete service warning
    //
    $("#delete").click(function () {
        var data = $("#servicetable").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected service?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected services?");
            }
            $('#warningOnDelete').modal('show')
        }
    })
);

