

function fitle_Null(str) {
    if(str == "null" || str == null || str == "None"){
        return "&nbsp;"
    }else return str
}

//初始化分页
$('#orderPage').bPage({
    url: 'search_picking_list.rpy',
    //开启异步处理模式
    asyncLoad: true,
    //关闭服务端页面模式
    serverSidePage: false,
    //数据自定义填充
    render: function (data) {
        var tb = $('#orderListTable tbody');
        $(tb).empty();
        if (data && data.list && data.list.length > 0) {
            $.each(data.list, function (i, row) {
                var tr = $('<tr>');
                $(tr).append('<td>'+(i+1)+'</td>');
                $(tr).append('<td>' + fitle_Null(row.job_num) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.picking_time) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.picking_type) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.operator_name) + '</td>');
                $(tb).append(tr);
            });
            $("#msg_info").text("查询完毕！");
        }else {
            $("#msg_info").text("未找到相关历史！");
        }
    },
    params: function () {
        return {
            job_num:$('#job_num').val(),
            operator_login:$('#operator_login').val(),
            picking_type:$('#picking_type').val(),
            picking_time_start:$('#picking_time_start').val(),
            picking_time_end:$('#picking_time_end').val()
        };
    }
});

function search_commit(){
    $("#msg_info").text("正在查询。。。");
    $('#orderPage').bPageRefresh();
    window.location='#list_mp';
}

//初始化日期选择
var fs = $('#picking_time_start').flatpickr({
    allowInput: true,
    maxDate:"today",
    locale: "zh",
    enableTime:true,
    time_24hr:true,
    dateFormat: "Y-m-d H:i",
    defaultDate:"08:00"
});

var fe = $('#picking_time_end').flatpickr({
    allowInput: true,
    maxDate:"today",
    locale: "zh",
    enableTime:true,
    time_24hr:true,
    dateFormat: "Y-m-d H:i",
    defaultDate:"21:00"
});


search_commit();
