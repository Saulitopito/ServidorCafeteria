#!/bin/bash
echo "Starting my app."
cd  /home/ubuntu/Sprint5
source venv/bin/activate
gunicorn --workers=20 -b 0.0.0.0:443 --certfile=micertificado.pem --keyfile=llaveprivada.pem wsgi:application