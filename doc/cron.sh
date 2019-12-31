#! /bin/bash
export PATH=$PATH:/usr/local/bin
cd /usr/local/workspace/rcl
# 动态
python3 run_djs.py  nohup > run_djs.log 2>&1  &
python3 run_dys.py  nohup > run_dys.log 2>&1  &
python3 run_eas.py  nohup > run_eas.log 2>&1  &
python3 run_ial.py  nohup > run_ial.log 2>&1  &
python3 run_matson.py  nohup > run_matson.log 2>&1  &
python3 run_namsung.py  nohup > run_namsung.log 2>&1  &
python3 run_pancon.py  nohup > run_pancon.log 2>&1  &
python3 run_tsl.py  nohup > run_tsl.log 2>&1  &
