#!/bin/bash
flask db upgrade
exec gunicorn app:app --bind 0.0.0.0:$PORT
