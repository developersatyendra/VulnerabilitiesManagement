var rowIDSelected = null;
$(document).ready(

    //
    // Declear serivces table
    //
    $(function () {
        $("#hosttable").bootstrapTable({
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
                  title: "IP Address",
                  field: "ipAdr",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Hostname",
                  field: "hostName",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Platform",
                  field: "platform",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "OS Name",
                  field: "osName",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Version",
                  field: "osVersion",
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
            url: "/hosts/api/gethosts",
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
    // Edit host
    //
    $('#hosttable').on('click-row.bs.table',function (e, row, element, field) {
        $('#id_hostName_edit').val(row.hostName);
        $('#id_ipAdr_edit').val(row.ipAdr);
        $('#id_platform_edit').val(row.platform);
        $('#id_osName_edit').val(row.osName);
        $('#id_osVersion_edit').val(row.osVersion);
        $('#id_description_edit').val(row.description);
        $('#editHostModal').modal('show');
        rowIDSelected = row.id;
        // var data = $('#editServicePostForm').serializeArray();
        // data.push({name: "id", value: row.id});
        // data = $.param(data)
        // alert(data);
        // alert(row);
        // var data = $(this).serializeArray(); ;
        // data.push({name: "id", value: 1});
        // data = $.param(data);
    }),
    $("#editHostPostForm").submit(function(e){
        var data = $('#editHostPostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updatehost", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.notification != null){
                notification.html(data.notification);
            }
            else{
                notification.html("The host is edited.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
            $("#hosttable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editServiceModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //
    // Add New Service
    //
    $("#addHostPostForm").submit(function(e){
        $.post("./api/addhost", $(this).serialize(), function(data){
            var notification = $("#retMsgAdd");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.notification != null){
                notification.html(data.notification);
            }
            else{
                notification.html("New Host is added.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
            $("#hosttable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#addHostModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete Host
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains Host ids
        var dataTable = $("#hosttable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deletehost', $.param(data),
             function(returnedData){
                if(returnedData.retVal > 0){
                    $('#warningOnDelete').modal('hide');
                    $("#hosttable").bootstrapTable('refresh');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete Host warning
    //
    $("#delete").click(function () {
        var data = $("#hosttable").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected Host?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected Hosts?");
            }
            $('#warningOnDelete').modal('show')
        }
    })
);

