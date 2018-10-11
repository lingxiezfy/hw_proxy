使用说明：
本项目包含以下4个程序以及其目录名，可分开部署
(一) 数据代理服务中心 -- proxy_server
(二) 消息分发中转站 -- result_server
(三) 扫描枪控制终端 -- scan_client
(四) 消息显示网页 -- www


(一) 数据代理服务中心 -- proxy_server
1. 日志
    日志按天存放在 proxy_server/log 目录下
2. 配置说明
    [proxyServer] -- 本程序使用的配置
        proxy_port=3390 -- 数据代理服务中心 运行的端口

