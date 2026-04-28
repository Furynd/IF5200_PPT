from itertools import product
import random
import time

from tqdm import tqdm

from backend.app.recommendation.optimizers import FangCollaborativeOptimizer
from backend.app.recommendation.scorers import FangVacancyScorer
from backend.app.repositories import ConfigRepository, UserRepository, VacancyRepository

class FangCollaborativeOptimizerUpdater:
    def __init__(
            self,
            user_repository: UserRepository,
            config_repository: ConfigRepository,
            collaborative_optimizer: FangCollaborativeOptimizer,
            verbose: bool = True,
            shuffle: bool = False
    ):
        self.user_repository = user_repository
        self.config_repository = config_repository
        self.collaborative_optimizer = collaborative_optimizer
        self.verbose = verbose
        self.shuffle = shuffle

    def update(self) -> None:
        user_ids = self.user_repository.get_all_user_ids()
        if len(user_ids) == 0:
            return
        
        max_train_error = self.config_repository.get_fang_max_train_error()
        max_train_steps = self.config_repository.get_fang_max_train_steps()

        user_count = len(user_ids)
        MAX_USER = 5
        if user_count > min(max_train_steps, MAX_USER):
            print(f"Warning: sampling is used because there are {user_count} user(s)")
            user_ids = random.sample(user_ids, k=min(max_train_steps, MAX_USER))
        elif self.shuffle:
            random.shuffle(user_ids)

        stop = False
        target_streak = len(user_ids)
        current_streak = 0
        step = 0

        pbar = tqdm(total=max_train_steps)

        if self.verbose:
            print("Start")
        start_time = time.time()
        while not stop:
            step += 1
            id = user_ids.pop(0)
            self.collaborative_optimizer.optimize(id)
            last_error = self.collaborative_optimizer.get_last_error()
            if last_error <= max_train_error:
                current_streak += 1
            else:
                current_streak = 0

            if self.verbose:
                current_time = time.time() - start_time
                print(id, f"{last_error=}", f"{current_streak=}", f"{current_time=}", sep="\t")

            pbar.update()

            if target_streak == current_streak or step == max_train_steps:
                pbar.close()
                stop = True
            else:
                user_ids.append(id)

        if self.verbose:
            current_time = time.time() - start_time
            print("Stop", f"{current_time=}", sep="\t")

class FangVacancyScorerUpdater:
    def __init__(
            self,
            scorer: FangVacancyScorer,
            user_repository: UserRepository,
            vacancy_repository: VacancyRepository,
            verbose=True,
    ):
        self.scorer = scorer
        self.user_repo = user_repository
        self.vacancy_repo = vacancy_repository
        self.verbose = verbose

    def update(self):
        user_id_list = self.user_repo.get_all_user_ids()
        vacancy_id_list = self.vacancy_repo.get_all_vacancy_ids()

        # Filter for the sake of easiness
        user_count = len(user_id_list)
        vacancy_count = len(vacancy_id_list)
        if user_count >= 10:
            if self.verbose:
                print(f"Warning: User is sampled because it's too many ({user_count})")
            user_id_list = random.sample(user_id_list, k=10)

        if vacancy_count >= 10:
            if self.verbose:
                print(f"Warning: Vacancy is sampled because it's too many ({vacancy_count})")
            vacancy_id_list = random.sample(vacancy_id_list, k=10)

        for user_id, vacancy_id in tqdm(product(user_id_list, vacancy_id_list), total=len(user_id_list) * len(vacancy_id_list)):
            score = self.scorer.get_score(user_id, vacancy_id)
            self.user_repo.set_vacancy_score(user_id, vacancy_id, score)
