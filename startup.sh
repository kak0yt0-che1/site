#!/bin/bash
flask db upgrade  # Применить миграции базы данных
exec gunicorn app:app --bind 0.0.0.0:$PORT
