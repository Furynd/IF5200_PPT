import os


def _normalize_database_url(raw_url: str) -> str:
    """Normalize variants so they work with sync SQLAlchemy engines."""
    database_url = raw_url.strip()

    # Legacy shorthand sometimes used in env files.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # Supabase examples often use asyncpg; this app uses sync SQLAlchemy.
    if database_url.startswith("postgresql+asyncpg://"):
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)

    return database_url


def _build_local_postgres_url() -> str:
    user = os.getenv("POSTGRES_USER", "referly_admin")
    password = os.getenv("POSTGRES_PASSWORD", "referly_secure_123")
    database = os.getenv("POSTGRES_DB", "referly_db")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"


def resolve_database_url() -> str:
    """
    Resolve DB URL with support for Supabase and local development.

    Priority:
    1) DB_MODE=supabase -> SUPABASE_DATABASE_URL or DATABASE_URL
    2) DB_MODE=local    -> local URL from POSTGRES_* envs
    3) DB_MODE=auto     -> DATABASE_URL, SUPABASE_DATABASE_URL, then local fallback
    """
    db_mode = os.getenv("DB_MODE", "auto").strip().lower()
    explicit_database_url = os.getenv("DATABASE_URL", "").strip()
    supabase_database_url = os.getenv("SUPABASE_DATABASE_URL", "").strip()

    if db_mode == "supabase":
        selected = supabase_database_url or explicit_database_url
        if not selected:
            raise ValueError(
                "DB_MODE=supabase requires SUPABASE_DATABASE_URL or DATABASE_URL to be set."
            )
        return _normalize_database_url(selected)

    if db_mode == "local":
        return _normalize_database_url(_build_local_postgres_url())

    if explicit_database_url:
        return _normalize_database_url(explicit_database_url)

    if supabase_database_url:
        return _normalize_database_url(supabase_database_url)

    return _normalize_database_url(_build_local_postgres_url())