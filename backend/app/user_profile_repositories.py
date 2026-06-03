from __future__ import annotations

import logging

from neo4j import AsyncDriver
from sqlalchemy.orm import Session

from app.models.schema import User
from app.services.user_graph import create_user_node

logger = logging.getLogger(__name__)


class UserProfileSyncRepository:
    """Repository that keeps Postgres user profile and Neo4j user node in sync."""

    def __init__(self, db: Session, neo4j_driver: AsyncDriver):
        self.db = db
        self.neo4j_driver = neo4j_driver

    async def upsert_from_auth(
        self,
        *,
        user_id: str,
        email: str,
        full_name: str | None = None,
        phone_number: str | None = None,
        password_hash: str | None = None,
        strict_graph_sync: bool = False,
    ) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()

        if user is None:
            user = User(
                id=user_id,
                email=email,
                full_name=full_name,
                phone_number=phone_number,
                password_hash=password_hash,
            )
            self.db.add(user)
        else:
            if user.email != email:
                user.email = email
            if full_name is not None:
                user.full_name = full_name
            if phone_number is not None:
                user.phone_number = phone_number
            if password_hash is not None:
                user.password_hash = password_hash

        self.db.commit()
        self.db.refresh(user)

        try:
            await self.sync_neo4j_user(user)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Neo4j user sync failed for %s: %s", user.id, exc)
            if strict_graph_sync:
                raise

        return user

    async def sync_neo4j_user(self, user: User) -> dict | None:
        return await create_user_node(
            self.neo4j_driver,
            user_id=user.id,
            full_name=user.full_name or "",
            phone_number=user.phone_number or "",
        )
