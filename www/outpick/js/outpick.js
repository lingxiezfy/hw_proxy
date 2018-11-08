var header_title = '外协收料';
var num_name = '生产单号';
var do_clear = true;
var do_sum = true;

var msg_max_count = 40;

function init() {
    var request = GetRequest();
    console.log(request);
    if(request['do_sum'] == 'false'){
        do_sum =  false
    }
    if (do_sum) {
        $('#success_num').removeClass('ele_hidden')
    } else {
        $('#success_num').addClass('ele_hidden')
    }
    if(request['do_clear'] == 'false'){
        do_clear = false
    }
    if (do_clear) {
        $('#clear_btn').removeClass('ele_hidden')
    } else {
        $('#clear_btn').addClass('ele_hidden')
    }

    $('.header_title').text(request['header_title']);
    $('.num_name').text(request['num_name'])

}

function GetRequest() {
    var url = location.search; //获取url中"?"符后的字串
    var theRequest = new Object();
    if (url.indexOf("?") != -1) {
        var str = url.substr(1);
        strs = str.split("&");
        for (var i = 0; i < strs.length; i++) {
            theRequest[strs[i].split("=")[0]] = decodeURI(strs[i].split("=")[1]);
        }
    }
    return theRequest;
}

init();

function do_out_sourcing_pick() {
    if ($('#scan_form input').val() == '') {
        add_error('view_panel', '请扫描或输入单号!');
    } else if ($('#user_info .status').val() == 0) {
        add_error('view_panel', '未登录，请先登录!');
    } else {
        $.ajax({
            url: "out_sourcing_pick_scan.rpy",
            cache: false,
            data: {job_num: $('#job_num').val(), uid: $('#user_info .uid').val(), pwd: $('#user_info .pwd').val()},
            dataType: "json",
            method: "POST",
            success: function (data) {
                if (data.code == 1) {
                    if (data.msg_type == 'error') {
                        add_error('view_panel', data.time + " - " + data.msg);
                    } else if (data.msg_type == 'info') {
                        add_msg('view_panel', data.time + " - " + data.msg);
                        if (do_sum) {
                            $('#success_num label').text(parseInt($('#success_num label').text()) + 1)
                        }
                    }else if(data.msg_type == 'warning'){
                        add_warning('view_panel', data.time + " - " + data.msg)
                    }
                } else if (data.code == 2) {
                    add_error('view_panel', '未登录，请刷新后重新登录!');
                } else {
                    add_error('view_panel', '非法访问！请联系管理!');
                }
            },
            error: function () {
                $('#loginModal .return_msg').val("连接失败！请重试")
            }
        })
    }
    $('#job_num').val('');
    $('#scan_form').submit(false);
}

function add_msg(panel_id, msg) {
    var panel_length = $('#' + panel_id + ' .panel-body').children("div").length;
    if (panel_length >= msg_max_count) {
        $('#' + panel_id + ' .panel-body').children("div")[panel_length - 1].remove()
    }
    $('#' + panel_id + ' .panel-body').prepend("<div>" + msg + " </div>");
}

function add_error(panel_id, error) {
    var panel_length = $('#' + panel_id + ' .panel-body').children("div").length;
    if (panel_length >= msg_max_count) {
        $('#' + panel_id + ' .panel-body').children("div")[panel_length - 1].remove()
    }
    $('#' + panel_id + ' .panel-body').prepend("<div style='color: red'>" + error + " </div>");
}

function add_warning(panel_id, warning) {
    var panel_length = $('#' + panel_id + ' .panel-body').children("div").length;
    if (panel_length >= msg_max_count) {
        $('#' + panel_id + ' .panel-body').children("div")[panel_length - 1].remove()
    }
    $('#' + panel_id + ' .panel-body').prepend("<div style='color: yellow'>" + warning + " </div>");
}

function clear_panel() {
    $('#job_num').val('');
    $('#success_num label').text('0');
    $('#view_panel .panel-body').html('');
    $('#scan_form').submit(false);
}

function user_login() {
    if ($('#usr').val() == '') {
        $('#loginModal .return_msg').text("请输入用户名")
    } else if ($('#pwd').val() == '') {
        $('#loginModal .return_msg').text("请输入密码")
    } else {
        $.ajax({
            url: "login.rpy",
            cache: false,
            data: $('#loginModal form').serialize(),
            dataType: "json",
            method: "POST",
            success: function (data) {
                if (data.code == 1) {
                    $('#loginModal .return_msg').text("登录成功");
                    $('#user_info .login_btn').addClass('ele_hidden');
                    $('#user_info .name').text("已登录： " + data.name);
                    $('#user_info .status').val(1);
                    $('#user_info .uid').val(data.uid);
                    $('#user_info .pwd').val(data.pwd);
                    $('#user_info .logout_btn').removeClass('ele_hidden');
                    $('#loginModal').modal('hide');
                } else if (data.code == 2) {
                    $('#loginModal .return_msg').text("用户名或密码错误！")
                } else {
                    $('#loginModal .return_msg').text("非法访问！请联系管理")
                }
            },
            error: function () {
                $('#loginModal .return_msg').val("连接失败！请重试")
            }
        })
    }
}

function user_logout() {
    $('#loginModal .return_msg').text("");
    $('#user_info .login_btn').removeClass('ele_hidden');
    $('#user_info .name').text("未登录");
    $('#user_info .status').val(0);
    $('#user_info .uid').val('-1');
    $('#user_info .pwd').val('-1');
    $('#user_info .logout_btn').addClass('ele_hidden');
    $('#loginModal input').val('');
}