from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import polars as pl
import pandas as pd
import numpy as np
import math


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
                n_jobs=-1
            )
            self.grid.fit(X_train, y_train)
            y_pred_train = self.grid.predict(X_train)
            y_pred = self.grid.predict(X_test)
        if self.scaler:
            x_scaler = StandardScaler()
            y_scaler = StandardScaler()
            X_scale = x_scaler.fit_transform(X_train)
            y_scale = y_scaler.fit_transform(y_train.reshape(-1, 1))
            x_test_scale = x_scaler.transform(X_test)
            self.model.fit(X_scale, y_scale)
            y_pred_scale = self.model.predict(x_test_scale)
            y_train_scale = self.model.predict(X_scale)
            y_pred_train = y_scaler.inverse_transform(y_train_scale)
            y_pred = y_scaler.inverse_transform(y_pred_scale)
        else:
            self.model.fit(X_train, y_train)
            y_pred_train = self.model.predict(X_train)
            y_pred = self.model.predict(X_test)
            # plot feature importance
        if self.grid_search:
            self.feature_importances = self.grid.best_estimator_.feature_importances_
            self._plot_feature_importance(x=range(X_train.shape[1]))
        else:
            self._plot_coef(coef=self.model.coef_)

        metrics = {
            "Model": self.model.__class__.__name__,
            'RMSE Train': round(math.sqrt(mean_squared_error(y_train, y_pred_train)), 4),
            'RMSE Test': round(math.sqrt(mean_squared_error(y_test, y_pred)), 4),
            'MAE Train': round(mean_absolute_error(y_train, y_pred_train), 4),
            'MAE Test': round(mean_absolute_error(y_test, y_pred), 4),
            'R2 Score Train': round(r2_score(y_train, y_pred_train), 4),
            'R2 Score Test': round(r2_score(y_test, y_pred), 4),
        }
        metrics = pl.DataFrame(metrics)
        print(metrics)
        return metrics

    def _plot_feature_importance(self, x):
        indices = np.argsort(self.feature_importances)[::-1]
        # plot feature importance and transpose to horizontal
        plt.figure(figsize=(10, 5))
        plt.title("Feature Importance")
        plt.bar(x, self.feature_importances[indices], align='center')
        plt.xticks(x, self.columns[indices], rotation=90)
        plt.tight_layout()
        plt.show()

    def _plot_coef(self, coef):
        coefs = pd.DataFrame(
            coef.T, index=self.columns, columns=["Coefficients"]
        )
        coefs.plot(kind="barh", figsize=(9, 7))
        plt.axvline(x=0, color=".5")
        plt.subplots_adjust(left=0.3)
