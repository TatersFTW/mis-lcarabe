# XAMPP MySQL Migration

1. Start Apache and MySQL in XAMPP.
2. Open phpMyAdmin and create a database named `realestate_db` with `utf8mb4_general_ci` collation.
3. Copy `.env.example` to `.env` and update the database values if your MySQL password is not blank.
4. Install dependencies:

```powershell
pip install -r requirements.txt
```

If `mysqlclient` fails on Windows, keep `PyMySQL` installed. The settings file automatically enables PyMySQL as a fallback.

5. Apply migrations:

```powershell
python manage.py migrate
```

6. Create a Broker account for administration:

```powershell
python manage.py createsuperuser
```

After creating the user, set `user_type` to `broker` in Django admin if needed. Do not rename the existing roles: Broker, Agent, and Buyer.

7. Optional SQLite data transfer:

Run these commands before switching `.env` to MySQL if you need to keep old SQLite data:

```powershell
python manage.py dumpdata --exclude auth.permission --exclude contenttypes > data.json
```

Then switch `.env` to MySQL, run migrations, and load:

```powershell
python manage.py loaddata data.json
```
