import numpy as np

from src.recommendation.fang import FangCollaborativeScorer, FangContentBasedScorer, FangSkill, FangUser, FangUserSkill, SkillSimilarityScorer

def test_fang_collaborative_scorer():
    user_latent_vector = np.random.randn(10)
    user_bias = np.random.randn()
    skill_latent_vector = np.random.randn(10)
    skill_bias = np.random.randn()
    global_bias = np.random.randn()
    expected_score = (
        global_bias
        + user_bias
        + skill_bias
        + np.dot(user_latent_vector,
                 skill_latent_vector)
    )
    expected_score = float(expected_score)
    max_error = 1e-8
    
    scorer = FangCollaborativeScorer()
    scorer.set_global_bias(global_bias)

    user_id = np.random.randint(999_999_999)
    user = FangUser(user_id)
    skill = FangSkill(
        np.random.randint(999_999_999),
        skill_latent_vector,
        skill_bias
    )
    # actual_score = scorer.get_score(user, skill)
    # assert abs(actual_score - expected_score) <= max_error

def test_fang_content_based_scorer_for_zero_user_skills():
    skill_id = np.random.randint(999_999_999)
    n_prev_user_skills = 1 + int(np.random.exponential(3))
    user_skills = []
    # for _ in range(n_prev_user_skills):
    #     user_skills.append(FangUserSkill(Fa))

    # expected_score = 0.0
    # max_error = 1e-8


    # class SimpleSkillSimilarityScorer(SkillSimilarityScorer):
    #     def get_score(self, first_skill: FangSkill, second_skill: FangSkill) -> float:
    #         return super().get_score(first_skill, second_skill)
    
    # scorer = FangContentBasedScorer()
    # scorer.set_global_bias(global_bias)

    # user = FangUser(
    #     np.random.randint(999_999_999),
    #     user_latent_vector,
    #     user_bias
    # )
    # skill = FangSkill(
    #     np.random.randint(999_999_999),
    #     skill_latent_vector,
    #     skill_bias
    # )
