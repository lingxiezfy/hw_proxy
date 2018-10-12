#!/bin/bash
work_path=$(cd "$(dirname "$0")"; pwd)
nohup `which python3` ${work_path}/route_proxy_client.py &
