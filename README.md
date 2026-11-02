# Expense Tracker API

A REST API to track personal expenses. Each user registers, logs in, and sees only their own expenses. Totals can be converted to another currency.

## Features

- Register and login (passwords hashed with bcrypt)
- JWT authentication (token valid for 15 minutes)
- Each user can only access their own expenses (other users' data returns 404)
- Create, list, update and delete expenses
- Total and monthly/category summary, converted to another currency
- Money is stored as `NUMERIC` and handled as `Decimal`, never float

## Tech stack

- Python 3.12
- FastAPI
- PostgreSQL with psycopg 3
- bcrypt and PyJWT
- httpx (async calls to the [Frankfurter](https://frankfurter.dev) exchange rate API)

## Setup

1. Clone the repo and create a virtual environment:

```bash
git clone https://github.com/houidi-yahya/expense-tracker.git
cd expense-tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Create the database and user in PostgreSQL:

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE expense_tracker;
CREATE USER expense_user WITH PASSWORD 'choose_a_strong_password';
\q
```

3. Create the tables, then give rights to the user (this order matters):

```bash
sudo -u postgres psql -d expense_tracker -f schema.sql
sudo -u postgres psql -d expense_tracker -f grant.sql
```

4. Create a `.env` file :

```
DB_HOST=localhost
DB_USER=expense_user
DB_PASSWORD=your_db_password
DB_NAME=expense_tracker
JWT_SECRET=your_long_random_secret
```

Generate a secret with:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## Run

Development (reloads on change):

```bash
fastapi dev main.py
```

Production:

```bash
fastapi run main.py --port 8000
```

Interactive docs: `http://127.0.0.1:8000/docs`

## Example usage

Register:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test12345!"}'
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test12345!"}'
```

Create an expense (use the `access_token` from login):

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"object":"coffee","price":"3.50","category":"food"}'
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | Get a JWT token |
| POST | `/expenses` | Create an expense |
| GET | `/expenses` | List your expenses |
| PUT / PATCH | `/expenses/{id}` | Replace / update an expense |
| DELETE | `/expenses/{id}` | Delete an expense |
| GET | `/expenses/total?currency=EUR` | Your total in another currency |
| GET | `/expenses/summary?currency=EUR` | Totals by month and by category |

All `/expenses` routes need the header `Authorization: Bearer <token>`.

## Deployment

Tested on an Ubuntu 24.04 server (Multipass VM): code cloned from GitHub, libraries in a virtual environment, PostgreSQL on the same machine, a `.env` file with its own secrets (permission `600`), and a `systemd` service that starts the app at boot and restarts it after a crash.

## Security notes

- Never commit `.env`. It is in `.gitignore`.
- Use a new `JWT_SECRET` for every environment.
- Passwords are hashed with bcrypt, never stored in clear text.
