

function fitle_Null(str) {
    if(str == "null" || str == null || str == "None"){
        return "&nbsp;"
    }else return str
}

//初始化分页
$('#orderPage').bPage({
    url: 'search_order_list.rpy',
    //开启异步处理模式
    asyncLoad: true,
    //关闭服务端页面模式
    serverSidePage: false,
    //数据自定义填充
    render: function (data) {
        var tb = $('#orderListTable tbody');
        $(tb).empty();
        var status_tb = $('#orderStatus tbody');
        $(status_tb).empty();
        var info_tb = $('#orderInfo tbody');
        $(info_tb).empty();
        if (data && data.list && data.list.length > 0) {
            var len = data.list.length;
            $.each(data.list, function (i, row) {
                var tr = $('<tr onclick="get_status(\'search_status.rpy\',\''+$.trim(row.OrdNumbH)+'\')">');
                $(tr).append('<td>'+(i+1)+'</td>');
                $(tr).append('<td>' + fitle_Null(row.CustNumb) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.Rectype) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.Reference) + '</td>');
                $(tr).append('<td>' + $.trim(row.OrdNumbH) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.ReqDelv) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.EntryDate) + '</td>');
                $(tr).append('<td>' + fitle_Null(row.Status) + '</td>');
                $(tb).append(tr);
            });
            $("#msg_info").text("已默认显示");
            if(len == 1){
                get_status('search_status.rpy',$.trim(data.list[0].OrdNumbH))
            }
        }else {
            $("#msg_info").text("未找到订单");
        }
    },
    params: function () {
        var CN = $('#CustNumb').val();
        var ONH =$('#OrdNumbH').val();
        var Re = $('#Reference').val();
        var S = $('#Status').val();
        var Sd = $('#EntryDate').val();
        return {
            CustNumb:CN,
            OrdNumbH:ONH,
            Reference:Re,
            Status:S,
            EntryDate:Sd
        };
    }
});

function search_commit(){

    $('#orderPage').bPageRefresh();
    window.location='#list_mp';
}

//初始化日期选择
var f = $('.flatpickr').flatpickr({
    allowInput: true,
    maxDate:"today",
    locale: "zh"
});


function get_status(url,job_num) {
    window.location = '#status_mp';
    $.ajax({
        url: url,
        data:{"job_num":job_num},
        async:true,
        method:"POST",
        dataType:"json",
        beforeSend:function(){
            $("#msg_info").text("正在查询 "+job_num);
        },
        success:function (data) {
            var status_tb = $('#orderStatus tbody');
            $(status_tb).empty();
            var info_tb = $('#orderInfo tbody');
            $(info_tb).empty();
            if (data && data.list && data.list.length > 0) {
                $.each(data.list, function (i, row) {
                    var tr = $('<tr>');
                    $(tr).append('<td>'+(i+1)+'</td>');
                    $(tr).append('<td>' + fitle_Null(row.job_num) + '</td>');
                    $(tr).append('<td>' + fitle_Null(row.description) + '</td>');
                    $(tr).append('<td>' + fitle_Null(row.operate_time) + '</td>');
                    $(tr).append('<td>' + fitle_Null(row.operator) + '</td>');
                    $(tr).append('<td>' + fitle_Null(row.deptment) + '</td>');
                    $(tr).append('<td>' + fitle_Null(row.matter) + '</td>');
                    $(tr).append('<td>' + fitle_Null(row.state) + '</td>');
                    $(status_tb).append(tr);
                });
                $("#msg_info").text("已查询 "+job_num+" 状态信息");
            }else {
                var tr = $('<tr>');
                if ($("#search_btn").attr('onclick') == "search_status_only()"){
                    $(tr).append('<td colspan="8" align="center" style="color: red;">未更新至历史订单，请查询&nbsp;<b>当前订单</b></td>');
                }else {
                    $(tr).append('<td colspan="8" align="center" style="color: red;"><b>无状态信息</b></td>');
                }

                $(status_tb).append(tr);
            }

            if (data && data.info && data.info.length > 0) {
                var R1 = $('<tr>');
                $(R1).append('<td>R</td>');
                var L1 = $('<tr>');
                $(L1).append('<td>L</td>');
                for(var i = 0;i<26;i++){
                    if(i % 2 == 0){
                        $(R1).append('<td>'+fitle_Null(data.info[i])+'</td>');
                    }else {
                        $(L1).append('<td>'+fitle_Null(data.info[i])+'</td>');
                    }
                }
                $(R1).append('<td rowspan="2">'+fitle_Null(data.info[26])+'</td>');

                var R2 = $('<tr>');
                $(R2).append('<td>R</td>');
                var r_dia = fitle_Null(data.info[31]);
                var r_tint = fitle_Null(data.info[33]);
                var r_lenname = fitle_Null(data.info[35]);
                $(R2).append('<td colspan="14"><b>'+
                    (r_lenname)+' ('+
                    fitle_Null(data.info[29])+
                    (r_dia == '&nbsp;'?r_dia:('&nbsp;/&nbsp;'+r_dia))+
                    (r_tint == '&nbsp;'?r_tint:('&nbsp;/&nbsp;'+r_tint))+')'+
                    '</b></td>');

                var L2 = $('<tr>');
                $(L2).append('<td>L</td>');
                var l_dia = fitle_Null(data.info[30]);
                var l_tint = fitle_Null(data.info[32]);
                var l_lenname = fitle_Null(data.info[36]);
                $(L2).append('<td colspan="14"><b>'+
                    (l_lenname)+' ('+
                    fitle_Null(data.info[28])+
                    (l_dia == '&nbsp;'?l_dia:('&nbsp;/&nbsp;'+l_dia))+
                    (l_tint == '&nbsp;'?l_tint:('&nbsp;/&nbsp;'+l_tint))+')'+

                    '</b></td>');

                var F = $('<tr>');
                $(F).append('<td>F</td>');
                var framename = fitle_Null(data.info[34]);
                $(F).append('<td colspan="14"><b>'+framename+'</b></td>');

                var Remark = $('<tr>');
                $(Remark).append('<td>Remark</td>');
                $(Remark).append('<td colspan="14" style="color: red">'+fitle_Null(data.info[27])+'</td>');

                $(info_tb).append(R1);
                $(info_tb).append(L1);
                $(info_tb).append(R2);
                $(info_tb).append(L2);
                $(info_tb).append(F);
                $(info_tb).append(Remark);

                $("#msg_info").text("已查询 "+job_num);
            }else {
                $("#msg_info").text("无订单信息");
            }
        },
        error:function () {
            $("#msg_info").text("网络连接不通");
        }
    })
}

function search_status_only() {

    job_num = $("#OrdNumbH").val();
    if(job_num==null || job_num ==""){
        $("#msg_info").text("请输入生产单号");
    }else {
        get_status('search_history.rpy',job_num)
    }

}

function now_order() {
    window.location.reload();


}

function hoistory_order() {
    $("#header_title").text("历史订单查询(3天前)");
    $("#order_list").hide();
    var status_tb = $('#orderStatus tbody');
    $(status_tb).empty();
    var info_tb = $('#orderInfo tbody');
    $(info_tb).empty();
    $("#search_btn").attr('onclick','search_status_only()');
    $(".hidden_true").hide();
    $("#msg_info").text("");
}

