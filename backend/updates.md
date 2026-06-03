## Setup Singkat

Backend:

1. Copy `backend/.env.example` ke `backend/.env`.
2. Isi minimal `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `FONNTE_API_KEY`, dan konfigurasi database.
3. Jalankan backend dari folder `backend/` sesuai environment yang dipakai project ini.

Frontend:

1. Masuk ke folder `frontend/`.
2. Install dependency jika perlu.
3. Jalankan `npm run build` untuk memastikan aplikasi React berhasil dikompilasi.

## Testing

- Backend tests: jalankan `pytest` dari root repository atau dari folder `backend/` setelah dependency tersedia.
- Frontend check: jalankan `npm run build` dari folder `frontend/`.
- Referral unit test yang ditambahkan bisa dijalankan dengan `pytest backend/tests/test_referral_delivery.py -q`.
- Beberapa test backend lama masih memerlukan Neo4j yang bisa di-resolve dari environment dan akan gagal jika service itu belum tersedia.

## Database migration for CV field

The code adds new columns to the `users` table to store CV metadata (`cv_filename`, `cv_url`, `cv_uploaded_at`). After pulling these changes, run the alembic migration from the `backend/` folder:

```bash
cd backend
alembic upgrade head
```

If you use the Docker compose setup, you can run migrations in the API container or run alembic locally against your database URL.

## Referral Flow

Referral sekarang memakai CV yang sudah diupload di halaman Profile (tersimpan di Supabase Storage dan metadata di tabel `users`), lalu mengirim pesan WhatsApp lewat Fonnte free berisi link CV tersebut.


------------------------------------------------------------------------------------------

feat: enhance authentication with Supabase integration and OAuth support

- Updated backend to support JWT decoding with both HS256 and JWKS methods.
- Added environment variables for Supabase configuration in backend and frontend.
- Introduced Supabase client in frontend for authentication and user management.
- Refactored authentication logic to handle OAuth login with Google and LinkedIn.
- Improved user session management and error handling during login and registration.
- Updated frontend components to reflect changes in authentication flow and user state.

------------------------------------------------------------------------------------------

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