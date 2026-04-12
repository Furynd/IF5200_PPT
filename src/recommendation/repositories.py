import numpy as np
import numpy.typing as npt

class FangCollaborativeParameterRepository:
    def get_global_bias(self) -> float:
        raise NotImplementedError
    
    def get_user_latent_vector(self, user_id: int) -> npt.NDArray[np.float64]:
        raise NotImplementedError
    
    def get_user_bias(self, user_id: int) -> float:
        raise NotImplementedError
    
    def get_skill_latent_vector(self, skill_id: int) -> npt.NDArray[np.float64]:
        raise NotImplementedError
    
    def get_skill_bias(self, skill_id: int) -> float:
        raise NotImplementedError
