#!/bin/bash
cd /var/tmp/applconn/
export FLASK_APP=applconn.py
flask run --host=0.0.0.0
