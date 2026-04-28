import os

from dotenv import load_dotenv
import neo4j
import numpy as np

from backend.app.repositories import ConfigRepository, FangCollaborativeParameterRepository, UserRepository, VacancyRepository

def prepare_neo4j_driver_and_database_name():
    load_dotenv()

    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j+s://xxxxx.databases.neo4j.io")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your-password-here")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

    driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    return driver, NEO4J_DATABASE

def is_unoccupied_config_id(driver: neo4j.Driver, config_id: int):
    records, _, _ = driver.execute_query(
        "MATCH (c:FangConfig {id: $id}) RETURN c;",
        id=config_id
    )
    return len(records) == 0

def is_unoccupied_user_id(driver: neo4j.Driver, user_id):
    records, _, _ = driver.execute_query(
        "MATCH (c:User {id: $id}) RETURN c;",
        id=user_id
    )
    return len(records) == 0

def is_unoccupied_skill_id(driver: neo4j.Driver, skill_id):
    records, _, _ = driver.execute_query(
        "MATCH (c:Skill {id: $id}) RETURN c;",
        id=skill_id
    )
    return len(records) == 0

def test_config_repository_get_fang_minimum_similarity():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_MIN_SIM = np.random.exponential()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    minimum_similarity: $minimum_similarity
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            minimum_similarity=CHOSEN_MIN_SIM
        )

        try:
            repo = ConfigRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_fang_minimum_similarity()
            assert result == CHOSEN_MIN_SIM
        finally:
            driver.execute_query("MATCH (c:FangConfig {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_config_repository_get_fang_learning_rate():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_LEARNING_RATE = np.random.exponential()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    learning_rate: $learning_rate
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            learning_rate=CHOSEN_LEARNING_RATE
        )

        try:
            repo = ConfigRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_fang_learning_rate()
            assert result == CHOSEN_LEARNING_RATE
        finally:
            driver.execute_query("MATCH (c:FangConfig {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_config_repository_get_fang_regularization_factor():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_REGULARIZATION_FACTOR = np.random.exponential()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    regularization_factor: $regularization_factor
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            regularization_factor=CHOSEN_REGULARIZATION_FACTOR
        )

        try:
            repo = ConfigRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_fang_regularization_factor()
            assert result == CHOSEN_REGULARIZATION_FACTOR
        finally:
            driver.execute_query("MATCH (c:FangConfig {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_config_repository_get_fang_max_train_error():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_MAX_TRAIN_ERROR = np.random.exponential()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    max_train_error: $max_train_error
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            max_train_error=CHOSEN_MAX_TRAIN_ERROR
        )

        try:
            repo = ConfigRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_fang_max_train_error()
            assert result == CHOSEN_MAX_TRAIN_ERROR
        finally:
            driver.execute_query("MATCH (c:FangConfig {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_config_repository_get_fang_max_train_steps():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_MAX_TRAIN_STEPS = 1 + int(np.random.exponential())
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    max_train_steps: $max_train_steps
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            max_train_steps=CHOSEN_MAX_TRAIN_STEPS
        )

        try:
            repo = ConfigRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_fang_max_train_steps()
            assert result == CHOSEN_MAX_TRAIN_STEPS
        finally:
            driver.execute_query("MATCH (c:FangConfig {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_config_repository_get_embeddings_id():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_EMBEDDINGS_ID = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    embeddings_id: $embeddings_id
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            embeddings_id=CHOSEN_EMBEDDINGS_ID
        )

        try:
            repo = ConfigRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_embeddings_id()
            assert result == CHOSEN_EMBEDDINGS_ID
        finally:
            driver.execute_query("MATCH (c:FangConfig {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_config_repository_get_latent_vector_dimension():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_LATENT_VECTOR_DIMENSION = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    latent_vector_dimension: $latent_vector_dimension
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            latent_vector_dimension=CHOSEN_LATENT_VECTOR_DIMENSION
        )

        try:
            repo = ConfigRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_latent_vector_dimension()
            assert result == CHOSEN_LATENT_VECTOR_DIMENSION
        finally:
            driver.execute_query("MATCH (c:FangConfig {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_user_repository_get_all_similar_skills():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        repo = UserRepository(driver, database=NEO4J_DATABASE)
        repo.get_all_similar_skills(
            id="user-012",
            skill_id="skill-002",
            embed_id=120,
            min_sim_score=0.87
        )
        # Make sure it's not error.

def test_user_repository_get_connections_no_connection():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)

    with driver:
        driver.execute_query(
            """
                CREATE (c:User {id: $id});
            """,
            database_=NEO4J_DATABASE,
            id=CHOSEN_USER_ID,
        )

        try:
            repo = UserRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_connections(CHOSEN_USER_ID)
            assert isinstance(result, list)
            assert len(result) == 0
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )

def test_user_repository_get_suggested_connections_no_connection():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)

    with driver:
        driver.execute_query(
            """
                CREATE (c:User {id: $id});
            """,
            database_=NEO4J_DATABASE,
            id=CHOSEN_USER_ID,
        )

        try:
            repo = UserRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_suggested_connections(CHOSEN_USER_ID)
            assert isinstance(result, list)
            assert len(result) == 0
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )

def test_user_repository_get_vacancies_from_target_current_companies():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_TARGET_USER_ID = np.random.randint(999_999_999)

    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (c:User {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    CREATE (c:User {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_TARGET_USER_ID,
            )

            repo = UserRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_vacancies_from_target_current_companies(
                CHOSEN_USER_ID,
                CHOSEN_TARGET_USER_ID
            )
            assert isinstance(result, list)
            assert len(result) == 0
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )
            driver.execute_query("MATCH (c:User {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_TARGET_USER_ID
            )

def test_user_repository_get_connections_for_specific_company():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_COMPANY_ID = np.random.randint(999_999_999)

    with driver:
        driver.execute_query(
            """
                CREATE (c:User {id: $id});
            """,
            database_=NEO4J_DATABASE,
            id=CHOSEN_USER_ID,
        )
        driver.execute_query(
            """
                CREATE (c:Company {id: $id});
            """,
            database_=NEO4J_DATABASE,
            id=CHOSEN_COMPANY_ID,
        )

        try:
            repo = UserRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_connections_for_specific_company(CHOSEN_USER_ID, CHOSEN_COMPANY_ID)
            assert isinstance(result, list)
            assert len(result) == 0
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )
            driver.execute_query("MATCH (c:Company {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_COMPANY_ID
            )

def test_user_repository_get_suggested_connections_for_specific_company():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_COMPANY_ID = np.random.randint(999_999_999)

    with driver:
        driver.execute_query(
            """
                CREATE (c:User {id: $id});
            """,
            database_=NEO4J_DATABASE,
            id=CHOSEN_USER_ID,
        )
        driver.execute_query(
            """
                CREATE (c:Company {id: $id});
            """,
            database_=NEO4J_DATABASE,
            id=CHOSEN_COMPANY_ID,
        )

        try:
            repo = UserRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_suggested_connections_for_specific_company(CHOSEN_USER_ID, CHOSEN_COMPANY_ID)
            assert isinstance(result, list)
            assert len(result) == 0
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )
            driver.execute_query("MATCH (c:Company {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_COMPANY_ID
            )

def test_user_repository_get_all_user_ids():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    
    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (c:User {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            repo = UserRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_all_user_ids()
            assert CHOSEN_USER_ID in result
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )

def test_user_repository_set_vacancy_score_set_once():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_VACANCY_ID = np.random.randint(999_999_999)
    CHOSEN_VACANCY_SCORE = np.random.random() * 5
    
    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (c:User {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    CREATE (c:Vacancy {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID,
            )
            repo = UserRepository(driver, database=NEO4J_DATABASE)
            repo.set_vacancy_score(CHOSEN_USER_ID, CHOSEN_VACANCY_ID, CHOSEN_VACANCY_SCORE)

            records, _, _ = driver.execute_query(
                "MATCH (:Vacancy {id: $vacancy_id})-[s:SUGGESTED_TO]->(:User {id: $user_id}) RETURN s.decided_at AS decided_at, s.score AS score;",
                vacancy_id=CHOSEN_VACANCY_ID,
                user_id=CHOSEN_USER_ID,
            )
            assert len(records) == 1
            assert records[0]["decided_at"] is not None
            assert abs(records[0]["score"] - CHOSEN_VACANCY_SCORE) <= 1e-8
            
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )
            driver.execute_query("MATCH (c:Vacancy {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID
            )

def test_user_repository_set_vacancy_score_set_twice():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_VACANCY_ID = np.random.randint(999_999_999)
    CHOSEN_VACANCY_SCORE = np.random.random() * 5
    
    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (c:User {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    CREATE (c:Vacancy {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID,
            )
            repo = UserRepository(driver, database=NEO4J_DATABASE)
            repo.set_vacancy_score(CHOSEN_USER_ID, CHOSEN_VACANCY_ID, np.random.random() * 5)
            repo.set_vacancy_score(CHOSEN_USER_ID, CHOSEN_VACANCY_ID, CHOSEN_VACANCY_SCORE)

            records, _, _ = driver.execute_query(
                "MATCH (:Vacancy {id: $vacancy_id})-[s:SUGGESTED_TO]->(:User {id: $user_id}) RETURN s.decided_at AS decided_at, s.score AS score;",
                vacancy_id=CHOSEN_VACANCY_ID,
                user_id=CHOSEN_USER_ID,
            )
            assert len(records) == 1
            assert records[0]["decided_at"] is not None
            assert abs(records[0]["score"] - CHOSEN_VACANCY_SCORE) <= 1e-8
            
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )
            driver.execute_query("MATCH (c:Vacancy {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID
            )

def test_user_repository_get_all_skills():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_LEVEL = 1 + np.random.randint(4)
    
    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (u:User {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    CREATE (s:Skill {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )
            driver.execute_query(
                """
                    MATCH (u:User {id: $user_id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (u)-[:HAS_SKILL {level: $level}]->(s);
                """,
                database_=NEO4J_DATABASE,
                user_id=CHOSEN_USER_ID,
                skill_id=CHOSEN_SKILL_ID,
                level=CHOSEN_SKILL_LEVEL
            )

            repo = UserRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_all_skills(CHOSEN_USER_ID)
            assert (CHOSEN_SKILL_ID, CHOSEN_SKILL_LEVEL) in result

            # records, _, _ = driver.execute_query(
            #     "MATCH (:Vacancy {id: $vacancy_id})-[s:SUGGESTED_TO]->(:User {id: $user_id}) RETURN s.decided_at AS decided_at, s.score AS score;",
            #     vacancy_id=CHOSEN_SKILL_ID,
            #     user_id=CHOSEN_USER_ID,
            # )
            # assert len(records) == 1
            # assert records[0]["decided_at"] is not None
            # assert abs(records[0]["score"] - CHOSEN_SKILL_LEVEL) <= 1e-8
            
        finally:
            driver.execute_query("MATCH (c:User {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID
            )
            driver.execute_query("MATCH (c:Skill {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID
            )

def test_vacancy_repository_get_all_vacancy_ids():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_VACANCY_ID = np.random.randint(999_999_999)
    
    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (c:Vacancy {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID,
            )
            repo = VacancyRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_all_vacancy_ids()
            assert CHOSEN_VACANCY_ID in result
        finally:
            driver.execute_query("MATCH (c:Vacancy {id: $id}) DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID
            )

def test_vacancy_repository_get_info():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_COMPANY_ID = np.random.randint(999_999_999)
    CHOSEN_VACANCY_ID = np.random.randint(999_999_999)
    CHOSEN_DESCRIPTION = f"description-{CHOSEN_VACANCY_ID}"
    CHOSEN_SOURCE_URL = f"url-{CHOSEN_VACANCY_ID}"
    
    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (c:Company {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_COMPANY_ID
            )

            driver.execute_query(
                """
                    CREATE (c:Vacancy {
                        id: $id,
                        description: $description,
                        source_url: $source_url
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID,
                description=CHOSEN_DESCRIPTION,
                source_url=CHOSEN_SOURCE_URL
            )

            driver.execute_query(
                """
                    MATCH (c:Company {id: $company_id})
                    MATCH (v:Vacancy {id: $vacancy_id})
                    CREATE (c)-[:OPENS]->(v)
                """,
                database_=NEO4J_DATABASE,
                company_id=CHOSEN_COMPANY_ID,
                vacancy_id=CHOSEN_VACANCY_ID,
            )

            repo = VacancyRepository(driver, database=NEO4J_DATABASE)
            company_id, description, source_url = repo.get_info(CHOSEN_VACANCY_ID)
            # What if the company is unknown? Maybe later.
            assert description == CHOSEN_DESCRIPTION
            assert source_url == CHOSEN_SOURCE_URL
            assert company_id == CHOSEN_COMPANY_ID
        finally:
            driver.execute_query("MATCH (c:Vacancy {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID
            )
            driver.execute_query("MATCH (c:Company {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_COMPANY_ID
            )

def test_vacancy_repository_get_required_skills():
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()
    CHOSEN_VACANCY_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_UNEXPECTED_SKILL_ID = np.random.randint(999_999_999)
    
    with driver:
        try:
            driver.execute_query(
                """
                    CREATE (v:Vacancy {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID,
            )
            driver.execute_query(
                """
                    CREATE (s:Skill {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )
            driver.execute_query(
                """
                    MATCH (v:Vacancy {id: $vacancy_id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (v)-[:REQUIRES]->(s);
                """,
                database_=NEO4J_DATABASE,
                vacancy_id=CHOSEN_VACANCY_ID,
                skill_id=CHOSEN_SKILL_ID,
            )

            driver.execute_query(
                """
                    CREATE (s:Skill {id: $id});
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_UNEXPECTED_SKILL_ID,
            )

            repo = VacancyRepository(driver, database=NEO4J_DATABASE)
            result = repo.get_required_skills(CHOSEN_VACANCY_ID)
            assert CHOSEN_SKILL_ID in result
            assert CHOSEN_UNEXPECTED_SKILL_ID not in result

        finally:
            driver.execute_query("MATCH (c:Vacancy {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_VACANCY_ID
            )
            driver.execute_query("MATCH (c:Skill {id: $id}) DETACH DELETE c;",
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID
            )
        
def test_fang_repository_get_global_bias_node_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        try:
            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_global_bias()
            assert isinstance(result, float)
            # Make sure it's run properly
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

def test_fang_repository_get_global_bias_property_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_GLOBAL_BIAS = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            global_bias=CHOSEN_GLOBAL_BIAS
        )

        try:
            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_global_bias()
            assert isinstance(result, float)
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )
    
def test_fang_repository_get_global_bias_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_GLOBAL_BIAS = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    global_bias: $global_bias
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            global_bias=CHOSEN_GLOBAL_BIAS
        )

        try:
            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_global_bias()
            assert result == CHOSEN_GLOBAL_BIAS
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID
            )

def test_fang_repository_set_global_bias_node_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_GLOBAL_BIAS = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."

        try:
            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_global_bias(CHOSEN_GLOBAL_BIAS)
            
            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id}) RETURN c;",
                id=CONFIG_ID,
            )
            assert abs(records[0]["c"]["global_bias"] - CHOSEN_GLOBAL_BIAS) <= 1e-8
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

def test_fang_repository_set_global_bias_node_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_GLOBAL_BIAS = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."\
        
        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id,
                    global_bias: $global_bias
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
            global_bias=np.random.randn()
        )

        try:
            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_global_bias(CHOSEN_GLOBAL_BIAS)
            
            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id}) RETURN c;",
                id=CONFIG_ID,
            )
            assert abs(records[0]["c"]["global_bias"] - CHOSEN_GLOBAL_BIAS) <= 1e-8
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

def test_fang_repository_set_global_bias_property_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_GLOBAL_BIAS = np.random.randint(999_999_999)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."\
        
        driver.execute_query(
            """
                CREATE (:FangConfig {
                    id: $id
                });
            """,
            database_=NEO4J_DATABASE,
            id=CONFIG_ID,
        )

        try:
            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_global_bias(CHOSEN_GLOBAL_BIAS)
            
            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id}) RETURN c;",
                id=CONFIG_ID,
            )
            assert abs(records[0]["c"]["global_bias"] - CHOSEN_GLOBAL_BIAS) <= 1e-8
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

def test_fang_repository_get_user_latent_vector_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )

            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_user_latent_vector(CHOSEN_USER_ID)
            assert isinstance(result, np.ndarray)
            assert result.shape == (CHOSEN_DIMENSION,)
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_get_user_latent_vector_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_USER_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_USER_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (u:User {id: $user_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(u);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
                latent_vector=CHOSEN_USER_LATENT_VECTOR.tolist(),
                dimension=CHOSEN_DIMENSION,
                bias=CHOSEN_USER_BIAS,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_user_latent_vector(CHOSEN_USER_ID)
            assert (np.abs(result - CHOSEN_USER_LATENT_VECTOR)).max() <= 1e-8
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_get_user_bias_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION,
            )

            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_user_bias(CHOSEN_USER_ID)
            assert isinstance(result, float)
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_get_user_bias_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_USER_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_USER_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (u:User {id: $user_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(u);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
                latent_vector=CHOSEN_USER_LATENT_VECTOR.tolist(),
                dimension=CHOSEN_DIMENSION,
                bias=CHOSEN_USER_BIAS,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_user_bias(CHOSEN_USER_ID)
            assert abs(result - CHOSEN_USER_BIAS) <= 1e-8
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_get_skill_latent_vector_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION,
            )

            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_skill_latent_vector(CHOSEN_SKILL_ID)
            assert isinstance(result, np.ndarray)
            assert result.shape == (CHOSEN_DIMENSION,)
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

def test_fang_repository_get_skill_latent_vector_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_SKILL_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_SKILL_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION,
            )

            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(s);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                skill_id=CHOSEN_SKILL_ID,
                latent_vector=CHOSEN_SKILL_LATENT_VECTOR.tolist(),
                dimension=CHOSEN_DIMENSION,
                bias=CHOSEN_SKILL_BIAS,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_skill_latent_vector(CHOSEN_SKILL_ID)
            assert (np.abs(result - CHOSEN_SKILL_LATENT_VECTOR)).max() <= 1e-8
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

def test_fang_repository_get_skill_bias_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION,
            )

            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_skill_bias(CHOSEN_SKILL_ID)
            assert isinstance(result, float)
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

def test_fang_repository_get_skill_bias_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_SKILL_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_SKILL_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION,
            )

            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(s);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                skill_id=CHOSEN_SKILL_ID,
                latent_vector=CHOSEN_SKILL_LATENT_VECTOR.tolist(),
                dimension=CHOSEN_DIMENSION,
                bias=CHOSEN_SKILL_BIAS,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            result = repo.get_skill_bias(CHOSEN_SKILL_ID)
            assert (result - CHOSEN_SKILL_BIAS) <= 1e-8
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

def test_fang_repository_set_user_latent_vector_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_USER_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_USER_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_user_latent_vector(CHOSEN_USER_ID, CHOSEN_USER_LATENT_VECTOR)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(u:User {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
            )
            assert np.abs(np.array(records[0]["e"]["latent_vector"].to_native())
                          - CHOSEN_USER_LATENT_VECTOR).max() <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_set_user_latent_vector_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_USER_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_USER_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (u:User {id: $user_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(u);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
                latent_vector=np.random.randn(CHOSEN_DIMENSION),
                dimension=CHOSEN_DIMENSION,
                bias=np.random.randn(),
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_user_latent_vector(CHOSEN_USER_ID, CHOSEN_USER_LATENT_VECTOR)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(u:User {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
            )
            assert np.abs(np.array(records[0]["e"]["latent_vector"].to_native())
                          - CHOSEN_USER_LATENT_VECTOR).max() <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_set_user_bias_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_USER_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_USER_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            # driver.execute_query(
            #     """
            #         MATCH (c:FangConfig {id: $id})
            #         MATCH (u:User {id: $user_id})
            #         CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(u);
            #     """,
            #     database_=NEO4J_DATABASE,
            #     id=CONFIG_ID,
            #     user_id=CHOSEN_USER_ID,
            #     latent_vector=np.random.randn(CHOSEN_DIMENSION),
            #     dimension=CHOSEN_DIMENSION,
            #     bias=np.random.randn(),
            # )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_user_bias(CHOSEN_USER_ID, CHOSEN_USER_BIAS)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(u:User {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
            )
            assert abs(records[0]["e"]["bias"] - CHOSEN_USER_BIAS) <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_set_user_bias_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_USER_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_USER_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_USER_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_user_id(driver, CHOSEN_USER_ID), "User ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:User {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (u:User {id: $user_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(u);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
                latent_vector=np.random.randn(CHOSEN_DIMENSION),
                dimension=CHOSEN_DIMENSION,
                bias=np.random.randn(),
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_user_bias(CHOSEN_USER_ID, CHOSEN_USER_BIAS)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(u:User {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_USER_ID,
            )
            assert abs(records[0]["e"]["bias"] - CHOSEN_USER_BIAS) <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:User {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_USER_ID,
            )

def test_fang_repository_set_skill_latent_vector_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_SKILL_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_SKILL_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )
            # driver.execute_query(
            #     """
            #         MATCH (c:FangConfig {id: $id})
            #         MATCH (s:Skill {id: $skill_id})
            #         CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(s);
            #     """,
            #     database_=NEO4J_DATABASE,
            #     id=CONFIG_ID,
            #     skill_id=CHOSEN_SKILL_ID,
            #     latent_vector=np.random.randn(CHOSEN_DIMENSION),
            #     dimension=CHOSEN_DIMENSION,
            #     bias=np.random.randn(),
            # )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_skill_latent_vector(CHOSEN_SKILL_ID, CHOSEN_SKILL_LATENT_VECTOR)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(s:Skill {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_SKILL_ID,
            )
            assert np.abs(np.array(records[0]["e"]["latent_vector"].to_native())
                          - CHOSEN_SKILL_LATENT_VECTOR).max() <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

def test_fang_repository_set_skill_latent_vector_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_SKILL_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_SKILL_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(s);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                skill_id=CHOSEN_SKILL_ID,
                latent_vector=np.random.randn(CHOSEN_DIMENSION),
                dimension=CHOSEN_DIMENSION,
                bias=np.random.randn(),
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_skill_latent_vector(CHOSEN_SKILL_ID, CHOSEN_SKILL_LATENT_VECTOR)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(s:Skill {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_SKILL_ID,
            )
            assert np.abs(np.array(records[0]["e"]["latent_vector"].to_native())
                          - CHOSEN_SKILL_LATENT_VECTOR).max() <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

def test_fang_repository_set_skill_bias_relation_not_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_SKILL_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_SKILL_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )
            # driver.execute_query(
            #     """
            #         MATCH (c:FangConfig {id: $id})
            #         MATCH (s:Skill {id: $skill_id})
            #         CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(s);
            #     """,
            #     database_=NEO4J_DATABASE,
            #     id=CONFIG_ID,
            #     skill_id=CHOSEN_SKILL_ID,
            #     latent_vector=np.random.randn(CHOSEN_DIMENSION),
            #     dimension=CHOSEN_DIMENSION,
            #     bias=np.random.randn(),
            # )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_skill_bias(CHOSEN_SKILL_ID, CHOSEN_SKILL_BIAS)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(s:Skill {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_SKILL_ID,
            )
            assert abs(records[0]["e"]["bias"] - CHOSEN_SKILL_BIAS) <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )

def test_fang_repository_set_skill_bias_relation_exists():
    np.random.seed(120)
    CONFIG_ID = np.random.randint(999_999_999)
    CHOSEN_SKILL_ID = np.random.randint(999_999_999)
    CHOSEN_DIMENSION = np.random.randint(10)
    CHOSEN_SKILL_LATENT_VECTOR = np.random.randn(CHOSEN_DIMENSION)
    CHOSEN_SKILL_BIAS = np.random.randn()
    driver, NEO4J_DATABASE = prepare_neo4j_driver_and_database_name()

    with driver:
        assert is_unoccupied_config_id(driver, CONFIG_ID), "Config ID is already occupied; change your seed."
        assert is_unoccupied_skill_id(driver, CHOSEN_SKILL_ID), "Skill ID is already occupied; change your seed."

        try:
            driver.execute_query(
                """
                    CREATE (:FangConfig {
                        id: $id,
                        latent_vector_dimension: $dimension
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                dimension=CHOSEN_DIMENSION
            )
            driver.execute_query(
                """
                    CREATE (:Skill {
                        id: $id
                    });
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    MATCH (s:Skill {id: $skill_id})
                    CREATE (c)-[:ASSIGNS_PARAMETERS {latent_vector: vector($latent_vector, $dimension, FLOAT), bias: $bias}]->(s);
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
                skill_id=CHOSEN_SKILL_ID,
                latent_vector=np.random.randn(CHOSEN_DIMENSION),
                dimension=CHOSEN_DIMENSION,
                bias=np.random.randn(),
            )

            repo = FangCollaborativeParameterRepository(driver, config_id=CONFIG_ID, database=NEO4J_DATABASE)
            repo.set_skill_bias(CHOSEN_SKILL_ID, CHOSEN_SKILL_BIAS)

            records, _, _ = driver.execute_query(
                "MATCH (c:FangConfig {id: $id})-[e:ASSIGNS_PARAMETERS]->(s:Skill {id: $user_id}) RETURN e",
                id=CONFIG_ID,
                user_id=CHOSEN_SKILL_ID,
            )
            assert abs(records[0]["e"]["bias"] - CHOSEN_SKILL_BIAS) <= 1e-8
            
        finally:
            driver.execute_query(
                """
                    MATCH (c:FangConfig {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CONFIG_ID,
            )

            driver.execute_query(
                """
                    MATCH (c:Skill {id: $id})
                    DETACH DELETE c;
                """,
                database_=NEO4J_DATABASE,
                id=CHOSEN_SKILL_ID,
            )
