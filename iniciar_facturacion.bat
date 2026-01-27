@echo off
title Django - Facturacion
cd /d C:\Proyectos\Facturacion

call venv\Scripts\activate

REM (Opcional) esperar 2 segundos por si Postgres tarda un poco
timeout /t 2 /nobreak >nul

python manage.py runserver 127.0.0.1:8000

pause
