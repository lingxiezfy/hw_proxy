#!/bin/bash
kill -s 9 `ps -ef | grep proxy_server/proxy_server | grep -v grep | awk '{print $2}'`
