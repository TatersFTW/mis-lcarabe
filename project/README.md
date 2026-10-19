# L. C. Arabe Realty Django Capstone

A Django 6 real estate management system with Buyer, Agent, and Broker roles. It includes property listings, favorites, inquiries, reviews, partner logos, broker dashboards, seminars, and commission slips.

## Requirements

- Python 3.13
- XAMPP with MySQL/MariaDB running
- pip

## Setup

1. Open a terminal in this folder:

```powershell
cd "C:\Users\BETH ARABE\Desktop\Django capstone project\project"
```

2. Recreate the virtual environment if the bundled `.venv` does not start:

```powershell
python -m venv ..\.venv
..\.venv\Scripts\activate
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Copy the environment template:

```powershell
copy .env.example .env
```

The default `.env.example` is already configured for XAMPP MySQL:

```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=realestate_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

## Create The XAMPP Database

Use either option.

### Option A: phpMyAdmin Import

1. Start Apache and MySQL in XAMPP.
2. Open `http://localhost/phpmyadmin`.
3. Choose Import.
4. Import `database/realestate_db.sql`.

### Option B: Django Migrations

Create an empty `realestate_db` database in phpMyAdmin, then run:

```powershell
python manage.py migrate
```

## Run The App

```powershell
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Create Admin/Broker User

```powershell
python manage.py createsuperuser
```

After logging into `/admin/`, set the user type to `broker` if needed.

## Useful Commands

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

## Notes

- Uploaded files are stored in `media/`.
- Static source files are in `static/`; collected files go to `staticfiles/`.
- To temporarily use the bundled SQLite database, set:

```env
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```
