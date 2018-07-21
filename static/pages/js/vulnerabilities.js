var rowIDSelected = null;
$(document).ready(
    //
    // Decleare vulnerability table
    //
    $(function () {
        $("#vulntable").bootstrapTable({
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
                  title: "Scan Task",
                  field: "scanTask.name",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Host Scanned",
                  field: "hostScanned.hostName",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Service",
                  field: "service.name",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Level Risk",
                  field: "levelRisk",
                  align: "center",
                  valign: "middle",
                  sortable: true
                },
                {
                  title: "Summary",
                  field: "summary",
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
            url: "/vuln/api/getvulns",
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
    // Edit vuln
    //
    $('#vulntable').on('click-row.bs.table',function (e, row, element, field) {
        $('#id_levelRisk_edit').val(row.levelRisk);
        $('#id_scanTask_edit').val(row.scanTask.id);
        $('#id_summary_edit').val(row.summary);
        $('#id_hostScanned_edit').val(row.hostScanned.id);
        $('#id_service_edit').val(row.service.id);
        $('#id_description_edit').val(row.description);
        var levelRisk = "#id_levelRisk_edit_" + row.levelRisk;
        $('#id_levelRisk_edit_0').removeAttr("checked");
        $(levelRisk).attr("checked","");
        $('#editVulnModal').modal('show');
        rowIDSelected = row.id;
    }),
    $("#editVulnPostForm").submit(function(e){
        var data = $('#editVulnPostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updatevuln", data, function(data){
            var notification = $("#retMsgEdit");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.notification != null){
                notification.html(data.notification);
            }
            else{
                notification.html("The vulnerability is edited.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
            $("#vulntable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editVulnModal").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //
    // Add New vuln
    //
    $("#addVulnPostForm").submit(function(e){
        $.post("./api/addvulns", $(this).serialize(), function(data){
            var notification = $("#retMsgAdd");
            var closebtn = '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
            notification.removeClass("hidden");
            if(data.notification != null){
                notification.html(data.notification);
            }
            else{
                notification.html("New vulnerability is added.");
                notification.removeClass("alert-danger");
                notification.addClass("alert-info");
            }
            notification.append(closebtn);
            $("#vulntable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#addServiceModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete vuln
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains vuln ids
        var dataTable = $("#vulntable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deletevuln', $.param(data),
             function(returnedData){
                if(returnedData.retVal > 0){
                    $('#warningOnDelete').modal('hide');
                    $("#vulntable").bootstrapTable('refresh');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete vuln warning
    //
    $("#delete").click(function () {
        var data = $("#vulntable").bootstrapTable('getSelections');
        if(data.length > 0){
            if(data.length == 1){
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected vulnerability?");
            }
            else{
                $('#msgOnDelete').text("Are you sure to delete " + data.length + " selected vulnerabilities?");
            }
            $('#warningOnDelete').modal('show')
        }
    })
);

