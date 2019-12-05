#! /bin/bash
export PATH=$PATH:/usr/local/bin
cd /usr/local/workspace/rcl
python3 run_djs.py  nohup >> run_djs.log 2>&1 & python3 run_dys.py  nohup >> run_dys.log 2>&1 & python3 run_eas.py  nohup >> run_eas.log 2>&1 & python3 run_gsl.py   nohup > run_gsl.log 2>&1 & python3 run_matson.py   nohup > run_matson.log 2>&1 &

