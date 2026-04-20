from backend.app.recommendation.optimizers import FangCollaborativeOptimizer
from backend.app.repositories import ConfigRepository, UserRepository

class FangVacancyScorerUpdater:
    def __init__(
            self,
            user_repository: UserRepository,
            config_repository: ConfigRepository,
            collaborative_optimizer: FangCollaborativeOptimizer
    ):
        self.user_repository = user_repository
        self.config_repository = config_repository
        self.collaborative_optimizer = collaborative_optimizer

    def update(self) -> None:
        user_ids = self.user_repository.get_all_user_ids()
        if len(user_ids) == 0:
            return
        
        max_train_error = self.config_repository.get_fang_max_train_error()
        max_train_steps = self.config_repository.get_fang_max_train_steps()

        stop = False
        target_streak = len(user_ids)
        current_streak = 0
        step = 0
        while not stop:
            step += 1
            id = user_ids.pop(0)
            self.collaborative_optimizer.optimize(id)
            last_error = self.collaborative_optimizer.get_last_error()
            if last_error <= max_train_error:
                current_streak += 1
            else:
                current_streak = 0

            if target_streak == current_streak or step == max_train_steps:
                stop = True
            else:
                user_ids.append(id)
