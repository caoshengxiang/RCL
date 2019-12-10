#! /bin/bash
export PATH=$PATH:/usr/local/bin
cd /usr/local/workspace/rcl

python3 run_djs.py  nohup > run_djs.log 2>&1  &
python3 run_djsstatic.py  nohup > run_djsstatic.log 2>&1  &
python3 run_dys.py  nohup > run_dys.log 2>&1  &
python3 run_dysstatic.py  nohup > run_dysstatic.log 2>&1  &
python3 run_eas.py  nohup > run_eas.log 2>&1  &
python3 run_easstatic.py  nohup > run_easstatic.log 2>&1  &
python3 run_ial.py  nohup > run_ial.log 2>&1  &
python3 run_ialstatic.py  nohup > run_ialstatic.log 2>&1  &
python3 run_matson.py  nohup > run_matson.log 2>&1  &
python3 run_namsung.py  nohup > run_namsung.log 2>&1  &
python3 run_namsungstatic.py  nohup > run_namsungstatic.log 2>&1  &
python3 run_pancon.py  nohup > run_pancon.log 2>&1  &
python3 run_panconstatic.py  nohup > run_panconstatic.log 2>&1  &
python3 run_tsl.py  nohup > run_tsl.log 2>&1  &
