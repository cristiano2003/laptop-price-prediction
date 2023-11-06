from model.evaluate import evaluate
from sklearn.ensemble import (
    RandomForestRegressor,
    VotingRegressor,
    GradientBoostingRegressor,
    StackingRegressor
)
from sklearn.linear_model import (
    LinearRegression,
    ElasticNetCV,
    RidgeCV,
    LassoCV

)

import pickle
import os
import numpy as np


class Model:
    def __init__(
        self,
        seed: int,
        checkpoint: str = None
    ):

        linear = LinearRegression()
        elastic = ElasticNetCV()
        ridge = RidgeCV()
        lasso = LassoCV()
        
        random_forest = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            criterion="friedman_mse",
            random_state=seed
        )

        gradient_boosting = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=10,
            criterion="friedman_mse",
            random_state=seed
        )

        voting = VotingRegressor(
            estimators=[
                ("lr", LinearRegression()),
                ("ridge", RidgeCV()),
                ("lasso", LassoCV()),
                ("elastic", ElasticNetCV())
            ],
            n_jobs=-1
        )

        stacking = StackingRegressor(
            estimators=[
                ("lr", LinearRegression()),
                ("ridge", RidgeCV()),
                ("lasso", LassoCV()),
                ("elastic", ElasticNetCV())
            ],
            n_jobs=-1
        )

        self.model_dict = {
            "linear": linear,
            "elastic": elastic,
            "ridge": ridge,
            "lasso": lasso,
            "random_forest": random_forest,
            "gradient_boosting": gradient_boosting,
            "voting": voting,
            "stacking": stacking
        }

        self.checkpoint = checkpoint

    def fit(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ):
        for name, model in self.model_dict.items():
            model.fit(X_train, y_train)

            y_pred = model.predict(X_test)
            df = evaluate(name, y_test, y_pred)
            print(df)

        self._save_model(name)

    def _save_model(self):
        if not os.path.exists(self.checkpoint):
            os.makedirs(self.checkpoint)
        with open(os.path.join(self.checkpoint, 'model.pkl'), 'wb') as f:
            pickle.dump(self.model_dict, f)
