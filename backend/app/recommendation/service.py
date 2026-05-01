from __future__ import annotations

try:
    from backend.app.repositories import UserRepository, VacancyRepository
except ImportError:  # pragma: no cover - fallback for package-root test execution
    from app.repositories import UserRepository, VacancyRepository


class RecommendationService:
    def __init__(self, user_repository: UserRepository, vacancy_repository: VacancyRepository):
        self.user_repository = user_repository
        self.vacancy_repository = vacancy_repository

    def get_connections(self, user_id):
        result = []
        for connected_user_id, score in self.user_repository.get_connections(user_id):
            result.append({"user_id": connected_user_id, "score": score})
        result.sort(key=lambda x: x["score"], reverse=True)

        return result
    
    def get_suggested_connections(self, user_id):
        result = []
        for connected_user_id, score in self.user_repository.get_suggested_connections(user_id):
            fof = True
            result.append({
                "user_id": connected_user_id,
                "score": score,
                "friend_of_friend": fof
            })
        result.sort(key=lambda x: (x["friend_of_friend"], x["score"]), reverse=True)

        return result
    
    def get_vacancies_from_target(self, user_id, target_user_id):
        result = []
        for vacancy_id, score in self.user_repository.get_vacancies_from_target_current_companies(user_id, target_user_id):
            company_id, description, source_url = self.vacancy_repository.get_info(vacancy_id)
            result.append({
                "company_id": company_id,
                "description": description,
                "source_url": source_url,
                "score": score,
            })

        result.sort(key=lambda x: x["score"], reverse=True)
        
        return result
    
    def get_connections_from_specific_company(self, user_id, company_id):
        result = []
        for connected_user_id, score in self.user_repository.get_connections_for_specific_company(user_id, company_id):
            result.append({"user_id": connected_user_id, "score": score})
        result.sort(key=lambda x: x["score"], reverse=True)

        return result
    
    def get_suggested_connections_from_specific_company(self, user_id, company_id):
        result = []
        for connected_user_id, score in self.user_repository.get_suggested_connections_for_specific_company(user_id, company_id):
            result.append({"user_id": connected_user_id, "score": score})
        result.sort(key=lambda x: x["score"], reverse=True)

        return result
