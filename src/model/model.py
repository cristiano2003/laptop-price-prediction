from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import (
    GradientBoostingRegressor,
    RandomForestRegressor,
    AdaBoostRegressor,
    BaggingRegressor
)
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.metrics import mean_absolute_error, mean_absolute_percentage_error, r2_score
import matplotlib.pyplot as plt
import polars as pl
import pandas as pd
import numpy as np
import math
import pickle


class LaptopPredictionModel:
    def __init__(
        self,
        model: str,
        columns: list,
        params: dict | None = None
    ):
        if model == "xgb":
            self.model = XGBRegressor()
            self.grid_search = True
            self.scaler = False
        elif model == "gdb":
            self.model = GradientBoostingRegressor()
            self.grid_search = True
            self.scaler = False
        elif model == "rdf":
            self.model = RandomForestRegressor()
            self.grid_search = True
            self.scaler = False
        elif model == "lnr":
            self.model = LinearRegression()
            self.grid_search = False
            self.scaler = True
        elif model == "ada":
            self.model = AdaBoostRegressor()
            self.grid_search = True
            self.scaler = False
        elif model == "bag":
            self.model = BaggingRegressor()
            self.grid_search = True
            self.scaler = False
        elif model == "sgd":
            self.model = SGDRegressor(max_iter=10000)
            self.grid_search = False
            self.scaler = True

        self.params = params
        self.columns = columns

    def fit(
        self,
        X_train: np.ndarray,
        X_test: np.ndarray,
        y_train: np.ndarray,
        y_test: np.ndarray
    ):
        print(f"Training {self.model.__class__.__name__}")
        if self.grid_search:
            self.grid = GridSearchCV(
                estimator=self.model,
                param_grid=self.params,
                cv=5,
                verbose=1,
                n_jobs=-1,
                refit=True,
            )
            self.grid.fit(X_train, y_train)
            y_pred_train = self.grid.predict(X_train)
            y_pred = self.grid.predict(X_test)
            self._save_model()
        if self.scaler:
            x_scaler = StandardScaler()
            X_scale = x_scaler.fit_transform(X_train)
            x_test_scale = x_scaler.transform(X_test)
            self.model.fit(X_scale, y_train)
            y_pred = self.model.predict(x_test_scale)
            y_pred_train = self.model.predict(X_scale)
        else:
            self.model.fit(X_train, y_train)
            y_pred_train = self.model.predict(X_train)
            y_pred = self.model.predict(X_test)
            # plot feature importance

        try:
            if self.grid_search:
                plt.figure(figsize=(20, 6))
                self.feature_importances = self.grid.best_estimator_.feature_importances_
                self._plot_feature_importance(x=range(X_train.shape[1]))
            else:
                plt.figure(figsize=(20, 6))
                self._plot_coef(coef=self.model.coef_)
        except:
            pass

        self._plot_regression(y_test, y_pred)
        plt.show()

        metrics = {
            "Model": self.model.__class__.__name__,
            'MAPE Train (%)': round(math.sqrt(mean_absolute_percentage_error(y_train, y_pred_train)), 4)*100,
            'MAPE Test (%)': round(math.sqrt(mean_absolute_percentage_error(y_test, y_pred)), 4)*100,
            'MAE Train': round(mean_absolute_error(y_train, y_pred_train), 4),
            'MAE Test': round(mean_absolute_error(y_test, y_pred), 4),
            'R2 Score Train': round(r2_score(y_train, y_pred_train), 4),
            'R2 Score Test': round(r2_score(y_test, y_pred), 4),
        }
        metrics = pl.DataFrame(metrics)
        print(metrics)
        return metrics

    def _plot_regression(self, y_test, y_pred):
        plt.subplot(1, 2, 2)
        plt.scatter(y_test, y_pred)
        plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', lw=4)
        plt.xlabel('Actual')
        plt.ylabel('Predicted')
        plt.title("Comparison")

    def _plot_feature_importance(self, x):
        plt.subplot(1, 2, 1)
        indices = np.argsort(self.feature_importances)[::-1]
        # plot feature importance and transpose to horizontal
        plt.title("Feature Importance")
        plt.bar(x, self.feature_importances[indices], align='center')
        plt.xticks(x, self.columns[indices], rotation=90)
        plt.tight_layout()

    def _plot_coef(self, coef):

        plt.subplot(1, 2, 1)
        coef = coef.squeeze()
        index = np.argsort(coef)
        coef = coef[index]
        coefs = pd.DataFrame(
            coef, index=self.columns[index], columns=["Coefficients"]
        )
        plt.title("Coefficients")
        plt.bar(coefs.index, coefs["Coefficients"])
        plt.xticks(rotation=90)

    def _save_model(self):
        # save the best model in grid search
        with open(f"./checkpoint/{self.model.__class__.__name__}.pkl", "wb") as f:
            pickle.dump(self.grid.best_estimator_, f)
