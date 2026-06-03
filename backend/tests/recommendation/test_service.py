from __future__ import annotations

from typing import Any

import numpy as np

from backend.app.repositories import UserRepository, VacancyRepository
from backend.app.recommendation.service import RecommendationService

def test_get_connections_unsorted():
    chosen_user_id = np.random.randint(999_999_999)
    connections: dict[int, float] = {}

    for _ in range(5 + int(np.random.exponential(5))):
        stop = False
        new_user_id = -1
        while not stop:
            new_user_id = np.random.randint(999_999_999)
            stop = (
                new_user_id != chosen_user_id
                and new_user_id not in connections
            )

        connections[new_user_id] = np.random.random()

    expected_result = [
        {
            "user_id": user_id,
            "score": score
        } for user_id, score in connections.items()
    ]
    expected_result.sort(key=lambda x: x["score"], reverse=True)

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_connections(self, id: int) -> list[tuple[int, float]]:
            assert id == chosen_user_id
            self._fetch()
            return [(k, v) for k, v in connections.items()]
        
    class MockVacancyRepository(VacancyRepository):
        def __init__(self):
            pass
        
    user_repo = MockUserRepository()
    vacancy_repo = MockVacancyRepository()

    service = RecommendationService(user_repo, vacancy_repo)
    actual_result = service.get_connections(chosen_user_id)

    assert len(actual_result) == len(expected_result)
    for actual_el, expected_el in zip(actual_result, expected_result):
        assert len(actual_el) == len(expected_el)
        for key, expected_value in expected_el.items():
            assert actual_el[key] == expected_value

def test_get_suggested_connections_unsorted():
    chosen_user_id = np.random.randint(999_999_999)
    suggested_connections: dict[int, tuple[float, bool]] = {}

    for _ in range(5 + int(np.random.exponential(5))):
        stop = False
        new_user_id = -1
        while not stop:
            new_user_id = np.random.randint(999_999_999)
            stop = (
                new_user_id != chosen_user_id
                and new_user_id not in suggested_connections
            )

        suggested_connections[new_user_id] = (np.random.random(), (np.random.random() < 0.5))

    expected_result = [
        {
            "user_id": user_id,
            "score": score,
            "friend_of_friend": fof
        } for user_id, (score, fof) in suggested_connections.items()
    ]
    expected_result.sort(key=lambda x: (int(x["friend_of_friend"]), x["score"]), reverse=True)

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_suggested_connections(self, id: int) -> list[tuple[int, float, bool]]:
            assert id == chosen_user_id
            self._fetch()
            return [(k, v, fof) for k, (v, fof) in suggested_connections.items()]
        
    class MockVacancyRepository(VacancyRepository):
        def __init__(self):
            pass
        
    user_repo = MockUserRepository()
    vacancy_repo = MockVacancyRepository()

    service = RecommendationService(user_repo, vacancy_repo)
    actual_result = service.get_suggested_connections(chosen_user_id)

    assert len(actual_result) == len(expected_result)
    for actual_el, expected_el in zip(actual_result, expected_result):
        assert len(actual_el) == len(expected_el)
        for key, expected_value in expected_el.items():
            assert actual_el[key] == expected_value

def test_get_vacancies_from_target():
    chosen_user_id = np.random.randint(999_999_999)
    chosen_target_user_id = np.random.randint(999_999_999)
    vacancy_infos: dict[int, tuple[int, str, str, float]] = {}

    for _ in range(5 + int(np.random.exponential(5))):
        stop = False
        new_vacancy_id = -1
        while not stop:
            new_vacancy_id = np.random.randint(999_999_999)
            stop = (
                new_vacancy_id != chosen_target_user_id
                and new_vacancy_id not in vacancy_infos
            )

        vacancy_infos[new_vacancy_id] = (
            np.random.randint(999_999_999),
            f"description{np.random.randint(999_999_999)}",
            f"url{np.random.randint(999_999_999)}",
            np.random.random(),
        )

    expected_result = [
        {
            "company_id": company_id,
            "description": description,
            "source_url": url,
            "score": score,
        } for company_id, description, url, score in vacancy_infos.values()
    ]
    expected_result.sort(key=lambda x: x["score"], reverse=True)

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_vacancies_from_target_current_companies(self, id, target_user_id) -> list[tuple[int, float]]:
            assert id == chosen_user_id
            assert target_user_id == chosen_target_user_id
            self._fetch()
            return [(vacancy_id, score) for vacancy_id, (_, _, _, score) in vacancy_infos.items()] 
        
    class MockVacancyRepository(VacancyRepository):
        def __init__(self):
            self.fetch_limit = len(vacancy_infos)

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1

        def get_info(self, id: int) -> tuple[int, str, str]:
            self._fetch()
            company_id, description, source_url, _ = vacancy_infos[id]
            return (company_id, description, source_url)
    
    user_repo = MockUserRepository()
    vacancy_repo = MockVacancyRepository()

    service = RecommendationService(user_repo, vacancy_repo)
    actual_result = service.get_vacancies_from_target(chosen_user_id, chosen_target_user_id)

    assert len(actual_result) == len(expected_result)
    for actual_el, expected_el in zip(actual_result, expected_result):
        assert len(actual_el) == len(expected_el)
        for key, expected_value in expected_el.items():
            assert actual_el[key] == expected_value

def test_get_connections_from_specific_company_unsorted():
    chosen_user_id = np.random.randint(999_999_999)
    chosen_company_id = np.random.randint(999_999_999)
    connections: dict[int, float] = {}

    for _ in range(5 + int(np.random.exponential(5))):
        stop = False
        new_user_id = -1
        while not stop:
            new_user_id = np.random.randint(999_999_999)
            stop = (
                new_user_id != chosen_user_id
                and new_user_id not in connections
            )

        connections[new_user_id] = np.random.random()

    expected_result = [
        {
            "user_id": user_id,
            "score": score
        } for user_id, score in connections.items()
    ]
    expected_result.sort(key=lambda x: x["score"], reverse=True)

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1
        
        def get_connections_for_specific_company(self, id, company_id) -> list[tuple[Any, float]]:
            assert id == chosen_user_id
            assert company_id == chosen_company_id
            self._fetch()
            return [(k, v) for k, v in connections.items()]
        
    class MockVacancyRepository(VacancyRepository):
        def __init__(self):
            pass
        
    user_repo = MockUserRepository()
    vacancy_repo = MockVacancyRepository()

    service = RecommendationService(user_repo, vacancy_repo)
    actual_result = service.get_connections_from_specific_company(chosen_user_id, chosen_company_id)

    assert len(actual_result) == len(expected_result)
    for actual_el, expected_el in zip(actual_result, expected_result):
        assert len(actual_el) == len(expected_el)
        for key, expected_value in expected_el.items():
            assert actual_el[key] == expected_value

def test_get_suggested_connections_from_specific_company_unsorted():
    chosen_user_id = np.random.randint(999_999_999)
    chosen_company_id = np.random.randint(999_999_999)
    connections: dict[int, float] = {}

    for _ in range(5 + int(np.random.exponential(5))):
        stop = False
        new_user_id = -1
        while not stop:
            new_user_id = np.random.randint(999_999_999)
            stop = (
                new_user_id != chosen_user_id
                and new_user_id not in connections
            )

        connections[new_user_id] = np.random.random()

    expected_result = [
        {
            "user_id": user_id,
            "score": score
        } for user_id, score in connections.items()
    ]
    expected_result.sort(key=lambda x: x["score"], reverse=True)

    class MockUserRepository(UserRepository):
        def __init__(self):
            self.fetch_limit = 1

        def _fetch(self):
            assert self.fetch_limit > 0
            self.fetch_limit -= 1
        
        def get_suggested_connections_for_specific_company(self, id, company_id) -> list[tuple[Any, float]]:
            assert id == chosen_user_id
            assert company_id == chosen_company_id
            self._fetch()
            return [(k, v) for k, v in connections.items()]
        
    class MockVacancyRepository(VacancyRepository):
        def __init__(self):
            pass
        
    user_repo = MockUserRepository()
    vacancy_repo = MockVacancyRepository()

    service = RecommendationService(user_repo, vacancy_repo)
    actual_result = service.get_suggested_connections_from_specific_company(chosen_user_id, chosen_company_id)

    assert len(actual_result) == len(expected_result)
    for actual_el, expected_el in zip(actual_result, expected_result):
        assert len(actual_el) == len(expected_el)
        for key, expected_value in expected_el.items():
            assert actual_el[key] == expected_value

