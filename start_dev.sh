#!/bin/bash
export PATH=/home/frappe/.nvm/versions/node/v24.15.0/bin:$PATH
cd /home/frappe/frappe-bench-v16/apps/brokerage_module/frontend
npm run dev -- --host 0.0.0.0 --port 8082
