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