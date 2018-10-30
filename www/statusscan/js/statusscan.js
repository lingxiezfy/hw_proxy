    var host = "192.168.1.214";
    var port = "6677";
    var msg_max_count = 40;


    function somebodyPanel(panel_id) {
        var oPanel = new Object();
        oPanel.panel_id = panel_id;

        oPanel.panel = $('#' + oPanel.panel_id + '');
        oPanel.reBtn = $('#' + oPanel.panel_id + ' .rc_btn');
        oPanel.conn_status = $('#' + oPanel.panel_id + ' .status');
        oPanel.reBtn.attr("onclick","reConnect('"+oPanel.panel_id+"')");
        oPanel.keepalive = 1;

        oPanel.ws = new WebSocket("ws://" + host + ":" + port + "");
        add_msg(oPanel.panel_id,"正在连接 - host: "+host+" - port: " +port);
        oPanel.ws.onopen = function (msg) {
            oPanel.ws.send("" + panel_id + "");
            add_msg(oPanel.panel_id,"连接成功");
            oPanel.panel.removeClass("panel-danger");
            oPanel.panel.addClass("panel-primary");
            oPanel.reBtn.attr("disabled","disabled");
            oPanel.conn_status.val(1);
            oPanel.heartCheck.start();
        };
        oPanel.ws.onmessage = function (msg) {
            if(msg.data.toString().indexOf('&') > 0){
                var msgs = msg.data.toString().split('&');
                for(var i = 0;i< msgs.length; i++){
                    deal_one_msg(oPanel.panel_id,msgs[i])
                }
            }else if(msg.data.toString() == "Pong"){
                oPanel.keepalive = 1;
            }else {
                deal_one_msg(oPanel.panel_id,msg.data)
            }
        };
        // oPanel.ws.onerror = function (msg){
        //     console.log("ss");
        //     console.log(WebSocket.CLOSED +":"+WebSocket.CLOSING+":"+WebSocket.CONNECTING+":"+WebSocket.OPEN)
        //     console.log(oPanel.ws.readyState);
        //     add_msg(oPanel.panel_id,"通讯失败");
        //     $('#' + oPanel.panel_id + '').removeClass("panel-primary");
        //     $('#' + oPanel.panel_id + '').addClass("panel-danger");
        // };
        oPanel.ws.onclose = function (msg) {
            add_error(oPanel.panel_id,"连接丢失,等待重连..");
            oPanel.panel.removeClass("panel-primary");
            oPanel.panel.addClass("panel-danger");
            oPanel.reBtn.removeAttr("disabled");
            oPanel.conn_status.val(-1);
            oPanel.heartCheck.clear();
            console.clear();
        };
        oPanel.heartCheck = {
            timeout: 60000,
            checkObj: null,
            timeoutObj: null,
            reset: function(){
                clearTimeout(this.timeoutObj);
                clearTimeout(this.checkObj);
                this.start();
            },
            start: function(){
                this.timeoutObj = setTimeout(function(){
                    oPanel.keepalive = 0;
                    oPanel.ws.send('Ping');
                    oPanel.heartCheck.check();
                }, this.timeout)
            },
            check: function () {
                this.checkObj = setTimeout(function(){
                    if(oPanel.keepalive == 1){
                        // console.log("check ok next");
                        oPanel.heartCheck.reset();
                    }else {
                        // console.log("check error close");
                        add_error(oPanel.panel_id, "与主机连接中断,请等待重连  - host:"+host+" - port:"+port);
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
        // console.log(msg);
        var first_sp =  msg.toString().indexOf(':');
        var op = msg.toString().substring(0,first_sp);
        var less_msg = msg.toString().substring(first_sp+1);
        if(op == "login"){
            $('#' + panel_id + ' .panel-title .login').text(less_msg.split(':')[0]+"("+less_msg.split(':')[1]+")")
        }else if(op == "state"){
            $('#' + panel_id + ' .panel-title .state').text(less_msg)
        }else if(op == "num"){
            $('#' + panel_id + ' .panel-title .num').text(less_msg+"")
        }else if(op == "cls"){
            $('#' + panel_id + ' .panel-body').children("div").remove()
        }else if(op == "msg"){
            add_msg(panel_id,less_msg)
        }else  if(op == "error"){
            add_error(panel_id,less_msg)
        }else if(op == "info"){
            add_info(panel_id,less_msg)
        }
    }

    function add_info(panel_id,info) {
        var panel_length = $('#' + panel_id + ' .panel-body').children("div").length;
        if (panel_length >= msg_max_count){
            $('#' + panel_id + ' .panel-body').children("div")[panel_length -1].remove()
        }
        $('#' + panel_id + ' .panel-body').prepend("<div style='color: #31b0d5'>"+info+" </div>");
    }
    function add_msg(panel_id,msg) {
        var panel_length = $('#' + panel_id + ' .panel-body').children("div").length;
        if (panel_length >= msg_max_count){
            $('#' + panel_id + ' .panel-body').children("div")[panel_length -1].remove()
        }
        $('#' + panel_id + ' .panel-body').prepend("<div>"+msg+" </div>");
    }
    function add_error(panel_id,error) {
        var panel_length = $('#' + panel_id + ' .panel-body').children("div").length;
        if (panel_length >= msg_max_count){
            $('#' + panel_id + ' .panel-body').children("div")[panel_length -1].remove()
        }
        $('#' + panel_id + ' .panel-body').prepend("<div style='color: red'>"+error+" </div>");
    }

    function reConnect(panel_id) {
        if($('#' + panel_id + ' .status').val() == -1){
            $('#' + panel_id + ' .status').val(0);
            somebodyPanel(panel_id)
        }else {
            add_error(panel_id, "已有正在尝试的连接，请等待...");
        }
    }

    var panel1 = somebodyPanel("mate_panel_1");
    var panel2 = somebodyPanel("mate_panel_2");
    var panel3 = somebodyPanel("mate_panel_3");
    var panel4 = somebodyPanel("mate_panel_4");

    function connect_loop(){
        if($('#mate_panel_1 .status').val() == -1){
            reConnect('mate_panel_1');
        }
        if($('#mate_panel_2 .status').val() == -1){
            reConnect('mate_panel_2');
        }
        if($('#mate_panel_3 .status').val() == -1){
            reConnect('mate_panel_3');
        }
        if($('#mate_panel_4 .status').val() == -1){
            reConnect('mate_panel_4');
        }
    }
    setInterval(connect_loop,5000);
