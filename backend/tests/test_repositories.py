import os

from dotenv import load_dotenv
import neo4j
import numpy as np

from backend.app.repositories import ConfigRepository, UserRepository

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