Add initial backend setup with database configurations and dependencies

- Create .gitignore for environment and cache files
- Add .env.example for environment variable configuration
- Set up Dockerfile for backend service
- Configure Alembic for database migrations
- Implement FastAPI application with health check endpoint
- Define SQLAlchemy models for User, Company, and ReferralRequest
- Create docker-compose.yml for service orchestration
- Initialize PostgreSQL, Neo4j, and Redis services
- Add init-db.sql for PostgreSQL extension setup
- Update requirements.txt with necessary dependencies

Recent updates (Auth, Profile, and Dev Flow)

- Add dev auth endpoints integration in API routing (`/api/auth/dev-register`, `/api/auth/dev-login`, `/api/auth/me`)
- Update dev register flow to accept JSON payload and persist basic profile fields (`full_name`, `phone_number`) into PostgreSQL
- Add password handling for dev auth:
	- Store password as `password_hash` during registration
	- Validate email + password on dev login
	- Return `401` for invalid credentials
- Sanitize auth responses to avoid leaking `password_hash` in login/register/me/sync responses
- Add resilient register behavior when Neo4j is unavailable:
	- PostgreSQL user creation remains successful
	- Neo4j user-node sync failure is logged as warning (best effort)
- Extend user schema with basic profile fields:
	- `full_name`
	- `phone_number`
- Add Alembic migration chain updates:
	- Add compatibility shim revision for missing historical revision (`b37e9b85722c`)
	- Add profile field migration (`8f3e0c1a7d2b`)
	- Add legacy password hash backfill migration (`c1d4a9e21f30`)
- Backfill legacy users with empty/null `password_hash` using default dev password support:
	- Default password: `dev12345`
	- Configurable via `DEV_LEGACY_BACKFILL_PASSWORD`
	- Hash salt/pepper configurable via `DEV_AUTH_PASSWORD_PEPPER`
- Update local dev environment alignment:
	- Frontend dev server moved to port `3000`
	- CORS updated to allow `http://localhost:3000`
	- Local PostgreSQL env defaults documented for docker compose

Related frontend integration updates

- Centralize token helpers in API client (`getToken`, `setToken`, `clearToken`)
- Improve API error parsing for FastAPI validation error arrays
- Update auth API calls to use dev endpoints (`/auth/dev-login`, `/auth/dev-register`)
- Store token on login and register; clear token on logout/401
- Update profile page to fetch `/auth/me` and render live `full_name`, `email`, and phone number