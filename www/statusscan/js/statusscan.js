var host = "localhost";
var port = 6677;
var msg_max_count = 40;
var panel_size = 1;
var min_width = 500;
var panel_list = new Array();

function init() {
    $.ajax({
        url: "config.rpy",
        cache: false,
        dataType: "json",
        method: "POST",
        timeout: 1500,
        success: function (data) {
            panel_size = data.panel_limit;
            min_width = data.min_width;
            host = data.ws_host;
            port = data.ws_port;
            var panel_index = 1;
            while (panel_index <= panel_size) {
                built_panel(panel_index);
                panel_index++;
            }
            make_panels()
        },
        error:function () {
            $('#panel_s').append('<div class="mate_panel" style="color: red;text-align: center"><span>获取配置失败，请刷新后再试！</span></div>>');
        }
    })
}

init();
$(window).resize(make_panels);
function make_panels() {
    var shight = $(window).height();
    var swidth = $(window).width();
    var col = build_row(panel_size, swidth);
    $('.mate_panel').css('width', 100 * (1 / col) + '%');
    var upset = panel_size % col;
    if (upset != 0) {
        $('#panel_' + panel_size).css('width', 100 * (1 - ((upset - 1) / col)) + '%')
    }
    var row = Math.ceil(panel_size / col);
    var head_hight = $('.panel-heading').height();
    var nav_height = $('nav').height();
    $('.height_nav').css('height', (nav_height+5) + 'px');
    var upset_height = shight - nav_height-5 - (row * head_hight)-((row)*45);
    if(upset_height > 0) {
        $('.mate_win_body').css('height', upset_height / row + 'px');
    }
};

function build_row(row_size, swidth) {
    while (row_size > 1) {
        var temp_w = swidth / row_size;
        if (temp_w < min_width) {
            row_size = row_size - 1;
        } else {
            break;
        }
    }
    return row_size
}

function built_panel(index) {
    panel_html = '<div id="panel_' + index + '" class="mate_panel">\n' +
        '                <div class="panel panel-danger">\n' +
        '                    <input class="status" type="hidden" value="0"/>\n' +
        '                    <input class="rc_flag" type="hidden" value="1"/>\n' +
        '                    <div class="panel-heading">\n' +
        '                        <h3 class="panel-title">\n' +
        '                            <span class="login">未登录()</span>&nbsp;-\n' +
        '                            总数:<span class="num">0</span>&nbsp;-\n' +
        '                            <span class="state">未扫状态条码</span>\n' +
        '                            <button class="btn btn-success btn-xs rc_btn">重新连接</button>\n' +
        '                        </h3>\n' +
        '                    </div>\n' +
        '                    <div class="panel-body mate_win_body body_overflow">\n' +
        '                    </div>\n' +
        '                </div>\n' +
        '            </div>';
    $('#panel_s').append(panel_html);
    var panel_id = 'panel_'+index
    panel_list.push(panel_id);
    somebodyPanel(panel_id)
}

function somebodyPanel(panel_id) {
    var oPanel = new Object();
    oPanel.panel_id = panel_id;

    oPanel.panel = $('#' + oPanel.panel_id + ' .panel');
    oPanel.reBtn = $('#' + oPanel.panel_id + ' .rc_btn');
    oPanel.conn_status = $('#' + oPanel.panel_id + ' .status');
    oPanel.reBtn.attr("onclick", "reConnect('" + oPanel.panel_id + "')");
    oPanel.keepalive = 1;
    oPanel.ws = new WebSocket("ws://" + host + ":" + port + "");
    cls(oPanel.panel_id);
    add_msg(oPanel.panel_id, "正在连接 - host: " + host + " - port: " + port);
    oPanel.ws.onopen = function (msg) {
        oPanel.ws.send("" + panel_id + "");
        add_msg(oPanel.panel_id, "连接成功 - 请登录");
        oPanel.panel.removeClass("panel-danger");
        oPanel.panel.addClass("panel-primary");
        oPanel.reBtn.attr("disabled", "disabled");
        oPanel.conn_status.val(1);
        oPanel.heartCheck.start();
    };
    oPanel.ws.onmessage = function (msg) {
        if (msg.data.toString().indexOf('&') > 0) {
            var msgs = msg.data.toString().split('&');
            for (var i = 0; i < msgs.length; i++) {
                deal_one_msg(oPanel.panel_id, msgs[i])
            }
        } else if (msg.data.toString() == "Pong") {
            oPanel.keepalive = 1;
        } else {
            deal_one_msg(oPanel.panel_id, msg.data)
        }
    };
    oPanel.ws.onclose = function (msg) {
        if($('#' + panel_id + ' .rc_flag').val() == 1) {
            add_error(oPanel.panel_id, "连接丢失,等待重连..");
        }
        oPanel.panel.removeClass("panel-primary");
        oPanel.panel.addClass("panel-danger");
        oPanel.reBtn.removeAttr("disabled");
        setLogin(oPanel.panel_id,'未登录()');
        setState(oPanel.panel_id,'未扫状态条码');
        setNum(oPanel.panel_id,'0');
        oPanel.conn_status.val(-1);
        oPanel.heartCheck.clear();
        console.clear();
    };
    oPanel.heartCheck = {
        timeout: 120000,
        checkObj: null,
        timeoutObj: null,
        reset: function () {
            clearTimeout(this.timeoutObj);
            clearTimeout(this.checkObj);
            this.start();
        },
        start: function () {
            this.timeoutObj = setTimeout(function () {
                oPanel.keepalive = 0;
                oPanel.ws.send('Ping');
                oPanel.heartCheck.check();
            }, this.timeout)
        },
        check: function () {
            this.checkObj = setTimeout(function () {
                if (oPanel.keepalive == 1) {
                    oPanel.heartCheck.reset();
                } else {
                    add_error(oPanel.panel_id, "与主机连接中断,请等待重连  - host:" + host + " - port:" + port);
                    oPanel.panel.removeClass("panel-primary");
                    oPanel.panel.addClass("panel-danger");
                    oPanel.heartCheck.clear();
                }
            }, this.timeout)
        },
        clear: function () {
            clearTimeout(this.timeoutObj);
            clearTimeout(this.checkObj);
        }
    };

    return oPanel;
}

function deal_one_msg(panel_id, msg) {
    var first_sp = msg.toString().indexOf(':');
    var op = msg.toString().substring(0, first_sp);
    var less_msg = msg.toString().substring(first_sp + 1);
    if (op == "login") {
        setLogin(panel_id,less_msg.split(':')[0] + "(" + less_msg.split(':')[1] + ")")
    } else if (op == "state") {
        setState(panel_id,less_msg)
    } else if (op == "num") {
        setNum(panel_id,less_msg + "")
    } else if (op == "cls") {
        cls(panel_id)
    } else if (op == "msg") {
        add_msg(panel_id, less_msg)
    } else if (op == "error") {
        add_error(panel_id, less_msg)
    } else if (op == "info") {
        add_info(panel_id, less_msg)
    } else if (op == "stop") {
        $('#' + panel_id + ' .rc_flag').val(0);
        add_error(panel_id, less_msg);
    }else {
        add_error(panel_id, msg)
    }
}
function setLogin(panel_id,login) {
    $('#' + panel_id + ' .panel-title .login').text(login);
}
function setState(panel_id,state) {
    $('#' + panel_id + ' .panel-title .state').text(state)
}
function setNum(panel_id,num) {
    $('#' + panel_id + ' .panel-title .num').text(num + "")
}
function cls(panel_id) {
    $('#' + panel_id + ' .panel-body').children("div").remove()
}
function add_info(panel_id, info) {
    var panel_length = $('#' + panel_id + ' .panel-body').children("div").length;
    if (panel_length >= msg_max_count) {
        $('#' + panel_id + ' .panel-body').children("div")[panel_length - 1].remove()
    }
    $('#' + panel_id + ' .panel-body').prepend("<div style='color: #31b0d5'>" + info + " </div>");
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

function reConnect(panel_id) {
    if($('#' + panel_id + ' .rc_flag').val() == 1){
        if ($('#' + panel_id + ' .status').val() == -1) {
            $('#' + panel_id + ' .status').val(0);
            somebodyPanel(panel_id)
        } else {
            add_error(panel_id, "已有正在尝试的连接，请等待...");
        }
    }else {
        add_error(panel_id, "已终止本窗口服务，请关闭本页面");
    }
}

function connect_loop(){
    var panel_index = 0;
    while (panel_index < panel_size) {
        var panel_id = panel_list[panel_index];
        if($('#' + panel_id + ' .rc_flag').val() == 1) {
            if ($('#' + panel_id + ' .status').val() == -1) {
                reConnect(panel_id);
            }
        }
        panel_index++;
    }
}
setInterval(connect_loop,10000);
