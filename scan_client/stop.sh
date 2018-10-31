#!/bin/bash
kill -s 9 `ps -ef | grep scan_client | grep -v grep | awk '{print $2}'`
