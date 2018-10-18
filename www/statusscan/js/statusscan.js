    var host = "localhost";
    var port = "6677";
    var msg_max_count = 40;

    function somebodyPanel(panel_id) {
        var oPanel = new Object();
        oPanel.panel_id = panel_id;
        oPanel.ws = new WebSocket("ws://" + host + ":" + port + "");
        oPanel.ws.onopen = function (msg) {
            oPanel.ws.send("" + panel_id + "");
            add_msg(oPanel.panel_id,"连接成功");

            $('#' + oPanel.panel_id + '').removeClass("panel-danger");
            $('#' + oPanel.panel_id + '').addClass("panel-primary");
            $('#' + oPanel.panel_id + ' .rc_btn').attr("disabled","disabled");
            $('#' + oPanel.panel_id + ' .status').val(1);
        };
        oPanel.ws.onmessage = function (msg) {
            if(msg.data.toString().indexOf('&') > 0){
                // console.log(msg.data);
                var msgs = msg.data.toString().split('&');
                for(var i = 0;i< msgs.length; i++){
                    deal_one_msg(oPanel.panel_id,msgs[i])
                }
            }else {
                deal_one_msg(oPanel.panel_id,msg.data)
            }
        };
        /*
        oPanel.ws.onerror = function (msg){
            console.log("ss");
            console.log(WebSocket.CLOSED +":"+WebSocket.CLOSING+":"+WebSocket.CONNECTING+":"+WebSocket.OPEN)
            console.log(oPanel.ws.readyState);
            add_msg(oPanel.panel_id,"连接失败");
            $('#' + oPanel.panel_id + '').removeClass("panel-primary");
            $('#' + oPanel.panel_id + '').addClass("panel-danger");
        };
        */
        oPanel.ws.onclose = function (msg) {
            add_msg(oPanel.panel_id,"连接丢失,等待重连..");
            $('#' + oPanel.panel_id + '').removeClass("panel-primary");
            $('#' + oPanel.panel_id + '').addClass("panel-danger");
            $('#' + oPanel.panel_id + ' .rc_btn').removeAttr("disabled");
            $('#' + oPanel.panel_id + ' .status').val(-1);
        };
        return oPanel;
    }
    panel1 = somebodyPanel("mate_panel_1");
    panel2 = somebodyPanel("mate_panel_2");
    panel3 = somebodyPanel("mate_panel_3");
    panel4 = somebodyPanel("mate_panel_4");

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
        add_error(panel_id, "正在重新连接-host:"+host+"-port:"+port);
        somebodyPanel(panel_id)
    }

    //全屏
    function fullScreen() {
        var el = document.documentElement;
        var rfs = el.requestFullScreen || el.webkitRequestFullScreen || el.mozRequestFullScreen || el.msRequestFullscreen;
        if (typeof rfs != "undefined" && rfs) {
            rfs.call(el);
        }

        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
        else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        }
        else if (document.webkitCancelFullScreen) {
            document.webkitCancelFullScreen();
        }
        else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
        if (typeof cfs != "undefined" && cfs) {
            cfs.call(el);
        }

        return;
    }

    //退出全屏
    function exitScreen() {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
        else if (document.mozCancelFullScreen) {
            document.mozCancelFullScreen();
        }
        else if (document.webkitCancelFullScreen) {
            document.webkitCancelFullScreen();
        }
        else if (document.msExitFullscreen) {
            document.msExitFullscreen();
        }
        if (typeof cfs != "undefined" && cfs) {
            cfs.call(el);
        }
    }

    function connect_roop(){
        if($('#mate_panel_1 .status').val() != 1){
            reConnect('mate_panel_1');
        }
        if($('#mate_panel_2 .status').val() != 1){
            reConnect('mate_panel_2');
        }
        if($('#mate_panel_3 .status').val() != 1){
            reConnect('mate_panel_3');
        }
        if($('#mate_panel_4 .status').val() != 1){
            reConnect('mate_panel_4');
        }
    }
    setInterval(connect_roop,5000);
