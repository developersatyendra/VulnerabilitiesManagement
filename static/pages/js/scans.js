var rowIDSelected = null;
$(document).ready(


    $(':file').on('fileselect', function(event, numFiles, label) {

          var input = $(this).parents('.input-group').find(':text'),
              log = numFiles > 1 ? numFiles + ' files selected' : label;

          if( input.length ) {
              input.val(log);
          } else {
              if( log ) alert(log);
          }

      }),
    //
    // Decleare scan tasks table
    //
    $(function () {
        $("#scanstable").bootstrapTable({
            columns:[
                {
                    field: 'state',
                    checkbox: true,
                    align: 'center',
                    valign: 'middle'
                },
                {
                    title: "Scan Task",
                    field: "name",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Is Processed",
                    field: "isProcessed",
                    align: "center",
                    valign: "middle",
                    formatter: BooleanFormatter,
                    sortable: true
                },
                {
                    title: "Start Time",
                    field: "startTime",
                    align: "center",
                    valign: "middle",
                    formatter: DateTimeFormater,
                    sortable: true
                },
                {
                    title: "Finished Time",
                    field: "endTime",
                    align: "center",
                    valign: "middle",
                    formatter: DateTimeFormater,
                    sortable: true
                },
                {
                    title: "Scan Project",
                    field: "scanProject.name",
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
            url: "/scans/api/getscans",
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
    $('#scanstable').on('click-row.bs.table',function (e, row, element, field) {
        $('#id_name_edit').val(row.name);
        if(row.isProcessed)
            $('#id_isProcessed_edit').attr("checked","");
        else
            $('#id_isProcessed_edit').removeAttr("checked");
        $('#id_description_edit').val(row.description);
        $('#id_startTime_edit').val(row.startTime.substring(0,row.startTime.length -1));
        $('#id_endTime_edit').val(row.endTime.substring(0,row.endTime.length -1));
        // $('#id_fileAttachment_edit').val(row.fileAttachment);
        $('#id_scanProject_edit').val(row.scanProject.id);
        $('#editScanModal').modal('show');
        rowIDSelected = row.id;
    }),
    $("#editScanPostForm").submit(function(e){
        var data = $('#editScanPostForm').serializeArray();
        data.push({name: "id", value: rowIDSelected});
        data = $.param(data);
        $.post("./api/updatescan", data, function(data){
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
            $("#scanstable").bootstrapTable('refresh');
        });
        e.preventDefault();
    }),
    $("#editScanPostForm").on("hidden.bs.modal", function () {
        $("#retMsgEdit").addClass("hidden");
    }),

    //
    // Add New scan
    //
    $("#addScanPostForm").submit(function(e){
        var formData = new FormData(this);
        $.ajax({
            url: "./api/addscan",
            type: 'POST',
            data: formData,
            success: function (data) {
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
                $("#scanstable").bootstrapTable('refresh');
            },
            cache: false,
            contentType: false,
            processData: false
        });
        e.preventDefault();
    }),
    $("#addScanModal").on("hidden.bs.modal", function () {
        $("#retMsgAdd").addClass("hidden");
    }),

    //
    // Confirm delete scan tasks
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains vuln ids
        var dataTable = $("#scanstable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deletescan', $.param(data),
             function(returnedData){
                if(returnedData.retVal > 0){
                    $('#warningOnDelete').modal('hide');
                    $("#scanstable").bootstrapTable('refresh');
                }
        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete scan tasks warning
    //
    $("#delete").click(function () {
        var data = $("#scanstable").bootstrapTable('getSelections');
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
$(document).on('change', ':file', function() {
    var input = $(this),
        numFiles = input.get(0).files ? input.get(0).files.length : 1,
        label = input.val().replace(/\\/g, '/').replace(/.*\//, '');
     input.trigger('fileselect', [numFiles, label]);
  });

// Format Datetime for bootstrap table
function DateTimeFormater(value, row, index) {
    date_t = new Date(value);
    return date_t.toLocaleString();
}

function BooleanFormatter(value, row, index){
    if(value){
        return '<b><i class="fa fa-check" aria-hidden="true"></i></b>';
    }
    else
        return '<b><i class="fa fa-remove" aria-hidden="true"></i></i></b>';
}