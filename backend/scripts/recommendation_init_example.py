import os

from dotenv import load_dotenv
import neo4j

from backend.app.recommendation.optimizers import FangCollaborativeOptimizer
from backend.app.recommendation.scorers import FangCollaborativeScorer, FangContentBasedScorer, FangScorer, FangVacancyScorer
from backend.app.recommendation.service import RecommendationService
from backend.app.recommendation.updaters import FangCollaborativeOptimizerUpdater, FangVacancyScorerUpdater
from backend.app.repositories import ConfigRepository, FangCollaborativeParameterRepository, UserRepository, VacancyRepository


def init():
    load_dotenv()
    CONFIG_ID = 120

    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://xxxxx.databases.neo4j.io")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

    user_repo = UserRepository(driver=driver, database=NEO4J_DATABASE)
    vacancy_repo = VacancyRepository(driver=driver, database=NEO4J_DATABASE)
    fang_repo = FangCollaborativeParameterRepository(driver=driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
    config_repo = ConfigRepository(driver=driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)

    service = RecommendationService(user_repository=user_repo, vacancy_repository=vacancy_repo)

    collaborative_scorer = FangCollaborativeScorer(fang_repo)
    content_based_scorer = FangContentBasedScorer(user_repo, config_repo)
    scorer = FangScorer(collaborative_scorer, content_based_scorer)
    vacancy_scorer = FangVacancyScorer(scorer, vacancy_repo)
    scorer_updater = FangVacancyScorerUpdater(vacancy_scorer, user_repo, vacancy_repo)

    optimizer = FangCollaborativeOptimizer(fang_repo, user_repo, config_repo)
    optimizer_updater = FangCollaborativeOptimizerUpdater(user_repo, config_repo, optimizer)

    return (
        service,           # Ini hubungkan ke API
        scorer_updater,    # Ini jalankan di background untuk interval fixed (misalkan per 1 menit)
        optimizer_updater, # Ini juga jalankan di background untuk interval fixed
    )
