from __future__ import annotations

import os

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.database import neo4j_driver
from app.recommendation.neo4j_repositories import Neo4jUserRepository, Neo4jVacancyRepository
from app.recommendation.service import RecommendationService
from app.repositories import UserRepository, VacancyRepository

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class MockUserRepository(UserRepository):
    def __init__(self):
        # user_id -> [(connected_user_id, score)]
        self._connections: dict[int, list[tuple[int, float]]] = {
            1: [(2, 0.95), (3, 0.73), (4, 0.68)],
            2: [(1, 0.95), (3, 0.70)],
            3: [(1, 0.73), (2, 0.70)],
        }
        # user_id -> [(suggested_user_id, score)]
        self._suggested_connections: dict[int, list[tuple[int, float]]] = {
            1: [(5, 0.82), (6, 0.76), (7, 0.60)],
            2: [(4, 0.67), (6, 0.64)],
            3: [(4, 0.71), (7, 0.58)],
        }
        # user_id -> [(vacancy_id, score)]
        self._vacancies: dict[int, list[tuple[int, float]]] = {
            1: [(1001, 0.91), (1002, 0.74), (1003, 0.66)],
            2: [(1003, 0.81), (1004, 0.77)],
            3: [(1002, 0.79), (1005, 0.72)],
        }

    def get_connections(self, id: int) -> list[tuple[int, float]]:
        return self._connections.get(id, [])

    def get_suggested_connections(self, id: int) -> list[tuple[int, float]]:
        return self._suggested_connections.get(id, [])

    def get_vacancies_from_current_companies(self, id: int) -> list[tuple[int, float]]:
        return self._vacancies.get(id, [])


class MockVacancyRepository(VacancyRepository):
    def __init__(self):
        # vacancy_id -> (company_id, description, source_url)
        self._vacancy_info: dict[int, tuple[int, str, str]] = {
            1001: (201, "Backend Engineer (Python/FastAPI)", "https://example.com/jobs/1001"),
            1002: (202, "Data Analyst (SQL, BI)", "https://example.com/jobs/1002"),
            1003: (203, "ML Engineer (NLP)", "https://example.com/jobs/1003"),
            1004: (204, "Frontend Engineer (React)", "https://example.com/jobs/1004"),
            1005: (205, "DevOps Engineer (Docker/K8s)", "https://example.com/jobs/1005"),
        }

    def get_info(self, id: int) -> tuple[int, str, str]:
        return self._vacancy_info.get(id, (0, "Unknown vacancy", ""))


def _build_recommendation_service() -> RecommendationService:
    user_repo = Neo4jUserRepository(neo4j_driver)
    vacancy_repo = Neo4jVacancyRepository(neo4j_driver)
    return RecommendationService(user_repo, vacancy_repo)


def get_recommendation_service() -> RecommendationService:
    # Defaults to real repositories, with optional mock fallback.
    use_mock = os.getenv("RECOMMENDATION_USE_MOCK", "false").lower() == "true"
    if use_mock:
        user_repo: UserRepository = MockUserRepository()
        vacancy_repo: VacancyRepository = MockVacancyRepository()
        return RecommendationService(user_repo, vacancy_repo)

    return _build_recommendation_service()


@router.get("/{user_id}/connections")
def get_connections(
    user_id: str,
    service: RecommendationService = Depends(get_recommendation_service),
):
    return {"connections": service.get_connections(user_id)}


@router.get("/{user_id}/suggested-connections")
def get_suggested_connections(
    user_id: str,
    service: RecommendationService = Depends(get_recommendation_service),
):
    return {"connections": service.get_suggested_connections(user_id)}


@router.get("/{user_id}/vacancies/from-target/{target_user_id}")
def get_vacancies_from_target(
    user_id: str,
    target_user_id: str,
    service: RecommendationService = Depends(get_recommendation_service),
):
    return {"vacancies": service.get_vacancies_from_target(user_id, target_user_id)}


@router.get("/{user_id}/connections/from-company/{company_id}")
def get_connections_from_specific_company(
    user_id: str,
    company_id: str,
    service: RecommendationService = Depends(get_recommendation_service),
):
    return {"connections": service.get_connections_from_specific_company(user_id, company_id)}


@router.get("/{user_id}/suggested-connections/from-company/{company_id}")
def get_suggested_connections_from_specific_company(
    user_id: str,
    company_id: str,
    service: RecommendationService = Depends(get_recommendation_service),
):
    return {"connections": service.get_suggested_connections_from_specific_company(user_id, company_id)}
