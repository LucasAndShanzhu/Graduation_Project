#!/usr/bin/bash
# echo $$ > /Users/gonglingxiao/var/pid/ip_sh.pid
index=0
while true
do 
    cd /home/lucas/Graduation_Project/infoflow/infoflow/spiders && python proxydbIp.py
    if [ $index == 2 ]
    then 
	   cd /home/lucas/Graduation_Project/infoflow && python run.py crawl nationip
           index=0
    else
           index=`expr $index + 1`
    fi
    sleep 300
done
