#!/bin/bash
# Выполнить миграции базы данных
flask db upgrade
# Запустить приложение
gunicorn app:app
