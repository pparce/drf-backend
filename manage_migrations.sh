#!/bin/bash


# Realiza las migraciones
python manage.py makemigrations
python manage.py migrate
