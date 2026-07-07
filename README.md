
Readme · MD
<h1 align="center">🧾 Sistema de Facturación</h1>
<p align="center">
  <b>A full-featured Django invoicing platform with 2FA, role-based access, audit logging and management reports.</b>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status">
  <img src="https://img.shields.io/badge/Django-5.2-092E20?style=flat-square&logo=django&logoColor=white" alt="Django">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="License">
</p>
---
 
## 📌 About the Project
 
**Sistema de Facturación** is a full-stack Django web application for small/medium businesses to
manage clients, suppliers, products, and electronic-style invoices — with a separate self-service
**client portal**, two-factor authentication (email OTP or Google Authenticator), full audit
logging of every create/edit/delete/login action, and a management dashboard with sales reports
and charts.
 
It was built as a real-world capstone project, covering everything from inventory and billing
logic to security (2FA, role isolation, audit trail) and PDF/Excel exports.
 
> ⚠️ **Note:** Actively maintained. Core billing, 2FA, auditing and reporting modules are complete
> and functional; new modules are added incrementally.
 
---
 
## ✨ Key Features
 
- 🧾 **Invoicing** — sequential numbering, SRI-style access key generation, automatic subtotal/IVA/discount/total calculation, invoice cancellation with automatic stock rollback.
- 📄 **PDF & Excel export** — invoices, clients, products, suppliers and categories, powered by WeasyPrint and openpyxl.
- 👤 **Client portal** — independent login for clients to view/download their own invoices and update their contact info.
- 🔐 **Two-factor authentication** — email OTP (SMTP) or Google Authenticator (TOTP), with a "trust this device" option.
- 🛡️ **Role-based access control** — `SuperAdmin`, `Vendedor` and `Clientes` groups, enforced by custom middleware that fully isolates each role's routes.
- 📝 **Audit trail** — every create/edit/delete/login/logout is logged with user, IP, user-agent and a before/after diff of changed fields.
- 📊 **Reporting dashboard** — sales by day/range, payment methods, top clients/products, category breakdown, cancelled invoices, seller ranking and profit margin, all with Chart.js visualizations.
- 🖼️ **Cloud image storage** — product images hosted on Cloudinary.
- 🌗 **Dark mode** — persistent light/dark theme across the admin panel and client portal.
---
 
## 🛠️ Tech Stack
 
The project follows a classic monolithic Django architecture, split into focused apps:
 
* **Backend:** **Django 5.2** (Python) — modular apps for clients, products, suppliers, categories, invoicing, reports, audit, users, and 2FA/TOTP.
* **Database:** **PostgreSQL**.
* **Frontend:** Django Templates + **Tailwind CSS**, **Lucide Icons**, **Chart.js**.
* **PDF generation:** **WeasyPrint**.
* **Spreadsheet export:** **openpyxl**.
* **Media storage:** **Cloudinary**.
* **2FA:** **pyotp** + **qrcode** (TOTP / Google Authenticator) and SMTP email OTP.
* **Deployment:** **Gunicorn** + **WhiteNoise**, hosted on **Render**.
---
 
## 📂 Project Structure
 
```
facturacion/
├── facturacion/          # Global settings, URLs, custom middleware
├── clientes/               # Clients + client self-service portal
├── productos/              # Product inventory (Cloudinary images)
├── categorias/             # Product categories
├── proveedores/            # Suppliers
├── facturacion_app/        # Core invoicing logic, PDF & Excel export
├── reportes/                # Management dashboard & reports
├── auditoria/               # Audit logging (signals + middleware)
├── usuarios/                 # Internal users, roles & permissions
├── twofa/                    # Email-based 2FA (OTP) + trusted devices
├── totp/                     # Google Authenticator (TOTP) 2FA
├── templates/                # Shared templates (base, auth, emails, reports)
├── static/                   # Static assets
├── build.sh                  # Render build script
└── manage.py
```
 
---
 
## 🚀 Getting Started
 
### Prerequisites
 
- Python 3.11+
- PostgreSQL 13+
- A [Cloudinary](https://cloudinary.com/) account (product images)
- An SMTP provider (e.g. [Brevo](https://www.brevo.com/)) for the email 2FA
- System dependencies for **WeasyPrint** (Linux):
```bash
  sudo apt-get install build-essential python3-dev python3-pip python3-setuptools \
      python3-wheel python3-cffi libpango-1.0-0 libpangoft2-1.0-0
```
 
### Installation
 
```bash
# 1. Clone the repo
git clone https://github.com/BryanRC99/Sistema_Facturacion.git
cd Sistema_Facturacion
 
# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / Mac
 
# 3. Install dependencies
pip install -r requirements.txt
 
# 4. Configure environment variables
cp .env.example .env         # then fill in your own values
 
# 5. Create the PostgreSQL database
#    CREATE DATABASE facturacion_pg;
 
# 6. Run migrations
python manage.py migrate
 
# 7. Create the required groups (SuperAdmin, Vendedor, Clientes)
python manage.py shell -c "
from django.contrib.auth.models import Group
[Group.objects.get_or_create(name=g) for g in ['SuperAdmin', 'Vendedor', 'Clientes']]
"
 
# 8. Create a superuser and assign it to the SuperAdmin group via /django-admin/
python manage.py createsuperuser
 
# 9. Run the development server
python manage.py runserver
```
 
| Portal | URL |
|---|---|
| Admin / Vendedor login | `http://127.0.0.1:8000/accounts/login/` |
| Client portal login | `http://127.0.0.1:8000/portal-clientes/login/` |
| Django admin | `http://127.0.0.1:8000/admin/` |
 
---
 
## ⚙️ Environment Variables
 
| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True` / `False` |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL credentials |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP config for email 2FA |
| `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Cloudinary credentials |
| `TRUST_DEVICE_DAYS` | Days a "trusted device" skips 2FA (default `30`) |
| `CREATE_SUPERUSER`, `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | Optional auto-created superuser on deploy |
 
---
 
## ☁️ Deployment (Render)
 
The repo ships with `build.sh`, used as the Render **Build Command**:
 
```bash
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```
 
**Start Command:** `gunicorn facturacion.wsgi`
 
1. Create a Web Service on Render pointing at this repo.
2. Attach a managed PostgreSQL instance.
3. Set all environment variables listed above in the Render dashboard.
4. Deploy 🚀
---
 
## 🗺️ Roadmap
 
- [ ] Move all sensitive config to environment variables (`django-environ` / `python-decouple`).
- [ ] Pin and commit a versioned `requirements.txt`.
- [ ] Add automated tests (currently scaffolded but empty per app).
- [ ] Document and expose a REST API (Django REST Framework is already installed).
- [ ] Basic CI (lint + tests) via GitHub Actions.
---
 
## 🤝 Contributing
 
This started as a personal/academic project, but suggestions, issues and pull requests are
welcome — feel free to open an issue if you'd like to discuss a feature or found a bug.
 
---
 
## 👤 Author
 
**Bryan Pineda**
📍 Quito, Ecuador · 📧 bryancr2004@gmail.com
🔗 [LinkedIn](https://www.linkedin.com/in/bryan-pineda-199610348/) · [GitHub](https://github.com/BryanRC99)
