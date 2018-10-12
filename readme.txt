使用说明：
本项目包含以下4个程序以及其目录名，可分开部署
(一) 扫描枪控制终端 -- scan_client
(二) 数据代理服务中心 -- proxy_server
(三) 消息分发中转站 -- result_server
(四) 消息显示网页（显示终端） -- www

程序部署
参照 部署拓扑图

获取ip说明
    Linux 获取本机ip命令：ifconfig -a
        找到 “inet addr” 即本机ip
    windows 获取本机ip命令：ipconfig
        找到 “IPV4地址” 即本机ip

(一) 扫描枪控制终端 -- scan_client
1. 功能说明
    同时控制多把扫描枪，将扫描数据发送至“数据代理服务中心”
    注：目前实现的是USB接口的输入方式
        当拔插扫描枪之后，等待3秒再进行扫描操作
2. 运行环境
    Linux系统
3. 配置说明
    [proxyServer] -- 需要连接的“数据代理服务中心”
        proxy_host=192.168.1.187 -- 运行数据代理服务中心的主机网络IP地址
            注：主机地址的获取需要先部署“数据代理服务中心”，使用系统命令获取本机IP，参照获取Ip说明
        proxy_port=3390 -- 数据代理服务中心 服务端口
            注：保持和数据代理服务中心（proxy_server）配置中的proxy_port一致
4. 日志
    日志按天存放在 scan_client/log目录下

(二) 数据代理服务中心 -- proxy_server
1. 功能说明
    接收所有“扫描枪控制终端”扫描的条码数据
    处理数据
    打包处理结果，并发送至“消息分发中转站”
2. 运行环境说明
    Linux、Windows
3. 配置说明
    [proxyServer] -- 数据代理服务中心运行的配置
        proxy_port=3390 -- 数据代理服务中心运行的端口
    [resultServer] -- 需要连接的“消息分发中转站”
        result_host=localhost -- 运行“消息分发中转站”的主机IP，ip的获取参照（一）中说明
            注，如果“数据代理服务中心” 和 “消息分发中转站” 部署在同一台主机上，为了提高传输效率result_host配置为localhost即可
        result_port=6690 -- 运行“消息分发中转站”的端口
    [MsSql] -- 旧的SQLServer数据库地址配置
    [Odoo] -- rpc地址配置，以及其他属性配置
    [input_path] -- 未配置显示位置的usb端口列表，有新的端口使用时，无需手动添加，在该端口插入扫描枪，并扫描数据之后，会自动在此节点添加
        192.168.1.121&pci-0000:00:1d.7-usb-0:1.2:1.0-event-kbd = #
        192.168.1.121&pci-0000:00:1d.7-usb-0:1.3:1.0-event-kbd = #
    [Route] -- 此节点配置usb输入端口数据的显示位置
        192.168.1.121&pci-0000:00:1a.7-usb-0:1.2:1.0-event-kbd = ws&192.168.1.187;mate_panel_3
        192.168.1.121&pci-0000:00:1a.7-usb-0:1.3:1.0-event-kbd = ws&192.168.1.187;mate_panel_4
        注：配置规则为 input_path = outer_panel
            为新的端口配置显示位置时，可扫描条码，配合日志文件来定位usb端口路径
                outer_panel 的格式 ：“ws&显示终端的ip&页面显示区域”
                显示终端ip说明
                    参照获取ip说明来获取
                页面显示区域说明
                    mate_panel_1，mate_panel_2，mate_panel_3，mate_panel_4 在web页面显示分表示为左上，右上，左下，右下四个显示区域
4. 日志
    日志按天存放在 proxy_server/log 目录下

(三) 消息分发中转站 -- result_server
1. 功能说明
    控制所有的显示终端
    接收由“数据代理服务中心”发送的结果数据包
    将结果数据发送至指定的显示终端
2  运行环境
    Linux、Windows
3. 配置说明
    [WebSocket] -- 附属WebSocket服务的配置
        ws_port=6677 -- WebSocket服务运行的端口
        panelLimit=4 -- 每一个显示终端连接支持的最大窗口数
    [resultServer] -- “消息分发中转站”的配置
        result_port=6690 -- 消息分发中转站 运行的端口
4. 日志
    日志按天存放在 result_server/log 目录下

(四) 消息显示网页（显示终端） -- www
1. 功能说明
    显示由“消息分发中转站”发送的结果消息
    注：目前实现的是Web页面显示，因此，需要有额外的web服务来提供该页面的web浏览
2. 运行环境
    Web浏览器，建议使用Chrome浏览器
3. 配置说明
   修改www\statusscan\js\statusscan.js文件中，关于WebSocket服务主机的ip和端口
   var host = "localhost"; -- 和“消息分发中转站” 网络ip一致，ip的获取参照 获取Ip说明
   var port = "6677"; -- 和“消息分发中转站” 中 ws_port 一致

