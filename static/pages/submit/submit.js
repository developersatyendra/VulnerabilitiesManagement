var rowIDSelected = null;
$(document).ready(
    //
    // Declear submit table
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
                    formatter:FilenameFormatter,
                    sortable: true
                },
                {
                    title: "Date Submit",
                    field: "dateCreated",
                    align: "center",
                    valign: "middle",
                    formatter: FormattedDate,
                    sortable: true
                },
                {
                    title: "Status",
                    field: "status",
                    align: "center",
                    valign: "middle",
                    sortable: true
                },
                {
                    title: "Scan Project",
                    field: "project.name",
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
                }

                // {
                //     title: "Description",
                //     field: "description",
                //     align: "center",
                //     valign: "middle",
                //     sortable: true
                // }
            ],
            // url: "/submit/api/getsubmits",
            // method: "get",
            idField: "id",
            ajax: ajaxRequest,
            striped: true,
            pagination: true,
            sidePagination: "server",
            pageList: [5, 10, 20, 50, 100, 200, 'All'],
            search: true,
        })

    }),

    //
    // Click Browse button
    //
    $('#btnBrowse').click(function () {
        $('#id_fileSubmitted').trigger('click');
    }),

    //
    // Click Browse Textbox
    //
    $('#fileUpload').click(function () {
        $('#id_fileSubmitted').trigger('click');
    }),

    //////////////////////////////////////////
    // Show file path on text input
    //
    $("#id_fileSubmitted").change(function (e) {
            $("#fileUpload").val(GetFileName($(this).val()));
        }
    ),

    //
    // Click cancel button
    //
    $("#cancelSubmitBtn").click(function () {
        $("#fileUpload").val("");
        $('#id_description').val("");
        $('#saveSubmitBtn').attr('disabled', true);
    }),
    //
    // Description on type
    //
    $('#id_description').on("input", function () {
        $('#saveSubmitBtn').attr('disabled', false);
    }),

    //
    // From add submit changes
    //
    $("#addSubmitPostForm").change(function () {
        $('#saveSubmitBtn').attr('disabled', false);
    }),

    //
    // Add New Submit
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
                if(data.status < 0){
                    title.text("Error");
                    body.text(data.message);
                }
                else{
                    $("#submittable").bootstrapTable('refresh');
                    title.text("Infomation");
                    body.text("File was submitted successfully")
                }
                $("#retInfoModal").modal('show');
                $("#servicetable").bootstrapTable('refresh');
                $('#saveSubmitBtn').attr('disabled', true);
            },
            cache: false,
            contentType: false,
            processData: false
        });
        e.preventDefault();
    }),

    //
    // Confirm delete service
    //
    $("#confirmDelete").click(function () {
        // Get csrf_token
        var csrf_token = $('meta[name="csrf-token"]').attr('content');

        // Create array contains submit ids
        var dataTable = $("#submittable").bootstrapTable('getSelections');
            var ids = new Array();
            for(i=0; i < dataTable.length; i++){
                ids.push(dataTable[i].id);
            }
        // Create array
        var data = [];
        data.push({name: "id", value: ids});
        data.push({name: "csrfmiddlewaretoken", value: csrf_token});
        $.post('./api/deletesubmit', $.param(data),
             function(returnedData){
                var body = $("#retInfoBody");
                var title = $("#retInfoTitle");
                if(returnedData.status == 0){
                    $('#warningOnDelete').modal('hide');
                    $("#submittable").bootstrapTable('refresh');
                    title.text("Information");
                }
                else{
                    title.text("Error");
                }
                body.text(returnedData.message);
                $("#retInfoModal").modal('show');

        }, 'json');
        $('#warningOnDelete').modal('hide')
    }),

    //
    // show delete submit warning
    //
    $("#delete").click(function () {
        var data = $("#submittable").bootstrapTable('getSelections');
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

// Get File name from path for bootstrap table
function FilenameFormatter(value, row, index){
    return value.replace(/^.*[\\\/]/, '');

}

// Get file name from path
function GetFileName(filepath) {
    if(filepath!==null){
        var fileNameIndex = filepath.lastIndexOf("/") + 1;
        var fileNameIndexWindows = filepath.lastIndexOf("\\") + 1;
        var filename = '';
        if(fileNameIndex != 0){
            filename =  filepath.substr(fileNameIndex);
        }
        else if(fileNameIndexWindows !=0){
            filename =  filepath.substr(fileNameIndexWindows);
        }
        else {
            return "";
        }
        return filename;
    }
    return "";
}

//////////////////////////////////////////
// Ajax get data to table
//
function ajaxRequest(params) {
    $.ajax({
        type: "GET",
        url: "/submit/api/getsubmits",
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