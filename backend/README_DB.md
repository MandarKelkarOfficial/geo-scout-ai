# Database Management

This project uses SQLAlchemy 2.0 with asynchronous drivers (`aiosqlite`) and Alembic for automated database migrations.

## Running Migrations

Before starting the server, ensure your database schema is up-to-date by applying the latest migrations.

1. Ensure your virtual environment is active.
2. Ensure your `DATABASE_URL` is properly set in your `.env` file (e.g. `sqlite+aiosqlite:///./geoai.db`).
3. Run Alembic upgrade:

```powershell
alembic upgrade head
```

This command will automatically run all pending migrations in `alembic/versions/` and seed any initial data (like the real estate listing cache).

## Generating New Migrations

If you make modifications to the data models in `app/db/models.py`, you must generate a new migration script to update the database schema.

```powershell
alembic revision --autogenerate -m "Description of changes"
```

Review the generated file in `alembic/versions/` to ensure Alembic correctly detected your changes before running `alembic upgrade head`.

## Switching to PostgreSQL

The models are written using database-agnostic SQLAlchemy 2.0 native Python types. No SQLite-specific types are used.

To migrate to PostgreSQL in the future:
1. Install the async driver: `pip install asyncpg`.
2. Change the `DATABASE_URL` in your `.env` file to point to your Postgres instance:
   `DATABASE_URL="postgresql+asyncpg://user:password@localhost/dbname"`
3. Run `alembic upgrade head` to recreate the schema in Postgres.
