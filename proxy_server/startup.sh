#!/bin/bash
work_path=$(cd "$(dirname "$0")"; pwd)
nohup `which python3` ${work_path}/reactor_proxy_server.py &