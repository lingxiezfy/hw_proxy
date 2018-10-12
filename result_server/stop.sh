#!/bin/bash
kill -s 9 `ps -ef | grep result_server/result_server | grep -v grep | awk '{print $2}'`
