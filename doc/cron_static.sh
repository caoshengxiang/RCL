#! /bin/bash
export PATH=$PATH:/usr/local/bin
cd /usr/local/workspace/rcl
# 静态
python3 run_djsstatic.py  nohup > run_djsstatic.log 2>&1  &
python3 run_dysstatic.py  nohup > run_dysstatic.log 2>&1  &
python3 run_easstatic.py  nohup > run_easstatic.log 2>&1  &
python3 run_ialstatic.py  nohup > run_ialstatic.log 2>&1  &
python3 run_namsungstatic.py  nohup > run_namsungstatic.log 2>&1  &
python3 run_panconstatic.py  nohup > run_panconstatic.log 2>&1  &
