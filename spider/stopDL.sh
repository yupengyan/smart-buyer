#!/bin/bash
cd "$(dirname "$0")"
#30:黑 31:红 32:绿 33:黄 34:蓝色 35:紫色 36:深绿 37:白色 
warn(){
    echo -e "\033[0;31;1m $(date "+%Y-%m-%d %H:%M:%S") [warn]: $1 \033[0m"
}

info(){
    echo -e "\033[0;32;1m $(date "+%Y-%m-%d %H:%M:%S") [info]: $1 \033[0m"
}

debug(){
    echo -e "\033[0;30;1m $(date "+%Y-%m-%d %H:%M:%S") [debug]: $1 \033[0m"
}

pkill_thread(){
    thread_name=$1
    force_stop=$2

    ps -efww | grep $thread_name | grep -v grep
    if [ $? -ne 0 ]; then
        warn "no thread named $thread_name"
        exit 1
    fi

    if $force_stop; then
        info 'force stop thread'
        ps -efww | grep $thread_name | grep -v grep | cut -c 9-15| xargs kill -9 2>/dev/null
    else
        ps -efww | grep $thread_name | grep -v grep | cut -c 9-15| xargs kill 2>/dev/null
    fi

    sleep 3
    ps -efww | grep $thread_name | grep -v grep
    if [ $? -eq 0 ]; then
        warn "fail stop all $thread_name thread"
    else
        info "succ stop $thread_name threads" 
    fi
}

force_stop=false
if [ $1 ];then
    force_stop=true
fi

project='dl-'
pkill_thread $project $force_stop
