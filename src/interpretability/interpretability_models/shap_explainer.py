# stdlib
import sys
import copy
from typing import Any, List, Tuple, Optional, Union
from abc import abstractmethod
from pathlib import Path
import os
import pickle as pkl

# third party
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt


# Interpretability relative
from .utils import data
from .base import Explainer, FeatureExplanation

# Interpretability absolute
from interpretability.utils.pip import install
from interpretability.exceptions.exceptions import ExplainCalledBeforeFit

# shap
for retry in range(2):
    try:
        # third party
        import shap

        break
    except ImportError:
        depends = ["shap"]
        install(depends)


class ShapExplainerBase(Explainer):
    def __init__(self, model, X_explain, y_explain, *argv, **kwargs) -> None:
        super(ShapExplainerBase, self).__init__(*argv, **kwargs)
        self.has_been_fit = True
        self.shap_values = None
        self.inner_explainer_save_path = None

    @staticmethod
    def type() -> str:
        return "explainer"

    def fit(self):
        print("SHAP explainers do not need to be fit. Please simply call explain().")

    def explain(self, *argv, **kwargs) -> pd.DataFrame:
        """
        The function to get the explanation data from the explainer
        """
        ...

    def summary_plot(
        self, explanation: List = None, show=True, save_path="temp_shap_plot.png"
    ):
        """
        Plot the feature importances using the shap summary_plot function.

        Args:
            explain_data (List): _description_
            explanation (_type_, optional): _description_. Defaults to None.
        """
        if not explanation:
            explanation = self.shap_values
        shap.summary_plot(explanation, self.explain_inputs, show=show)
        if not show:
            plt.savefig(save_path)

    # WATERFALL NOT WORKING
    # def plot_waterfall(self, class_idx, explanation: List = None):

    #     if not explanation:
    #         explanation = self.shap_values
    #     shap.plots.waterfall(explanation[class_idx])


class ShapKernelExplainer(ShapExplainerBase):
    """
    This is a light-weight wrapper for the kernel explainer from "SHAP", which is
    available from <https://github.com/slundberg/shap>.
    Additional functionality from the source class is accessible via the 'explainer'
    object.
    """

    def __init__(self, model, X_explain, y_explain, *argv, **kwargs) -> None:
        self.explain_inputs = X_explain
        self.explainer = shap.KernelExplainer(
            model, self.explain_inputs, *argv, **kwargs
        )

    @staticmethod
    def name() -> str:
        return "shap_kernel_explainer"

    @staticmethod
    def pretty_name() -> str:
        return "SHAP Kernel Explainer"

    @staticmethod
    def type() -> str:
        return "explainer"

    def explain(self, *argv, **kwargs) -> pd.DataFrame:
        """
        The function to get the explanation data from the explainer
        """
        self.shap_values = self.explainer.shap_values(
            self.explain_inputs, *argv, **kwargs
        )
        self.explanation = FeatureExplanation(self.shap_values)
        return self.explanation


class ShapGradientExplainer(ShapExplainerBase):
    """
    This is a light-weight wrapper for the Gradient explainer from "SHAP", which is
    available from <https://github.com/slundberg/shap>.
    Additional functionality from the source class is accessible via the 'explainer'
    object.
    """

    def __init__(self, model, X_explain, y_explain, *argv, **kwargs) -> None:
        self.explain_inputs = X_explain
        self.explainer = shap.GradientExplainer(
            model, self.explain_inputs, *argv, **kwargs
        )

    @staticmethod
    def name() -> str:
        return "shap_gradient_explainer"

    @staticmethod
    def pretty_name() -> str:
        return "SHAP Gradient Explainer"

    @staticmethod
    def type() -> str:
        return "explainer"

    def explain(self, *argv, **kwargs) -> pd.DataFrame:
        """
        The function to get the explanation data from the explainer
        """
        self.shap_values = self.explainer.shap_values(
            self.explain_inputs, *argv, **kwargs
        )
        self.explanation = FeatureExplanation(self.shap_values)
        return self.explanation


class ShapDeepExplainer(ShapExplainerBase):
    """
    This is a light-weight wrapper for the Deep explainer from "SHAP", which is
    available from <https://github.com/slundberg/shap>.
    Additional functionality from the source class is accessible via the 'explainer'
    object.
    """

    def __init__(self, model, X_explain, y_explain, *argv, **kwargs) -> None:
        explain_data = data.TabularDataset(X_explain, y_explain)
        explain_loader = DataLoader(
            explain_data, batch_size=len(y_explain), shuffle=True
        )
        self.explain_inputs, explain_targets = next(iter(explain_loader))
        self.explainer = shap.DeepExplainer(model, self.explain_inputs, *argv, **kwargs)

    @staticmethod
    def name() -> str:
        return "shap_deep_explainer"

    @staticmethod
    def pretty_name() -> str:
        return "SHAP Deep Explainer"

    @staticmethod
    def type() -> str:
        return "explainer"

    def explain(self, *argv, **kwargs) -> pd.DataFrame:
        """
        The function to get the explanation data from the explainer
        """
        self.shap_values = self.explainer.shap_values(
            self.explain_inputs, *argv, **kwargs
        )
        self.explanation = FeatureExplanation(self.shap_values)
        return self.explanation


class ShapTreeExplainer(ShapExplainerBase):
    """
    This is a light-weight wrapper for the Tree explainer from "SHAP", which is
    available from <https://github.com/slundberg/shap>.
    Additional functionality from the source class is accessible via the 'explainer'
    object.
    """

    def __init__(self, model, X_explain, *argv, **kwargs) -> None:
        self.explain_inputs = X_explain
        self.explainer = shap.TreeExplainer(model, X_explain, *argv, **kwargs)

    @staticmethod
    def name() -> str:
        return "shap_tree_explainer"

    @staticmethod
    def pretty_name() -> str:
        return "SHAP Tree Explainer"

    @staticmethod
    def type() -> str:
        return "explainer"

    def explain(self, *argv, **kwargs) -> pd.DataFrame:
        """
        The function to get the explanation data from the explainer
        """
        self.shap_values = self.explainer.shap_values(
            self.explain_inputs, *argv, **kwargs
        )
        self.explanation = FeatureExplanation(self.shap_values)
        return self.explanation


class ShapLinearExplainer(ShapExplainerBase):
    """
    This is a light-weight wrapper for the linear explainer from "SHAP", which is
    available from <https://github.com/slundberg/shap>.
    Additional functionality from the source class is accessible via the 'explainer'
    object.
    """

    def __init__(self, model, X_explain, *argv, **kwargs) -> None:
        self.explain_inputs = X_explain
        self.explainer = shap.LinearExplainer(model, X_explain, *argv, **kwargs)

    @staticmethod
    def name() -> str:
        return "shap_linear_explainer"

    @staticmethod
    def pretty_name() -> str:
        return "SHAP Linear Explainer"

    @staticmethod
    def type() -> str:
        return "explainer"

    def explain(self, X_explain=None, *argv, **kwargs) -> pd.DataFrame:
        """
        The function to get the explanation data from the explainer
        """

        self.shap_values = self.explainer.shap_values(
            self.explain_inputs, *argv, **kwargs
        )
        self.explanation = FeatureExplanation(self.shap_values)
        return self.explanation
