from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

@dataclass
class FangUser:
    id: int
    latent_vector: npt.ArrayLike
    bias: float

class FangUser:
    def __init__(self, id):
        self.id = ...

@dataclass
class FangSkill:
    id: int
    latent_vector: npt.ArrayLike
    bias: float

@dataclass
class FangUserSkill:
    skill: FangSkill
    level: float

class FangCollaborativeScorer:
    def __init__(self):
        self._global_bias = 0.0

    def set_global_bias(self, global_bias: float):
        self._global_bias = global_bias

    def get_global_bias(self):
        return self._global_bias

    def get_score(self, user: FangUser, skill: FangSkill):
        return (
            self.get_global_bias()
            + user.bias
            + skill.bias
            + np.dot(user.latent_vector,
                    skill.latent_vector)
        )

class SkillSimilarityScorer:
    """
    This is an abstract class, don't instantiate it.
    """

    def get_score(self, first_skill: FangSkill, second_skill: FangSkill) -> float:
        raise NotImplementedError

class FangContentBasedScorer:
    pass