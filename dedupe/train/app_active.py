from dedupe.base import BaseTrain

from collections import deque
from dataclasses import dataclass
from functools import cached_property
import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import seaborn as sns
sns.set(rc={'figure.figsize': (11.7, 8.27)})


@dataclass
class Active(BaseTrain):
    """
    Model to implement active learning
    """

    def __post_init__(self):
        self.labels = {}

    def initialize(self, X):
        self.X = X
        self.train(self.X, init=True)
        self.scores, self.y = self.fit(self.X)
        assert len(self.samples) > 0

    def init_y(self, size):
        return np.random.choice([0, 1], size=size, replace=True)

    def train(self, X, init=False, labels=None):
        X_scaled = StandardScaler().fit_transform(X)
        self.clf = SVC(kernel="linear", C=100, probability=True)
        if init:
            self.clf.fit(X_scaled, self.init_y(len(X)))
        else:
            self.clf.fit(X_scaled, labels)
        return self.clf

    @cached_property
    def samples(self):
        return {
            "low": deque(np.argsort(self.scores)),
            "high": deque(np.argsort(self.scores)[::-1]),
            "uncertain": deque(np.argsort(abs(self.scores - 0.5)))
        }

    @property
    def active_dict(self):
        return {
            int(x["idxmat_idx"]): x["label"] 
            for x in self.labels.values()
            if x["label"] in ["Yes", "No"]
        }

    def retrain(self):
        del self.samples
        self.train(
            self.X[list(self.active_dict.keys()), :], 
            init=False, 
            labels=list(self.active_dict.values())
        )
        self.scores, self.y = self.fit(self.X)
        assert len(self.samples) > 0

    def learn(self, df, X, candidates):
        self.initialize(X)
        self.run(candidates=candidates, df = df, _type="lowhigh")
        user_continue = True
        while user_continue:
            self.run(candidates=candidates, df = df, _type="uncertain")
            user_continue = input()

    def fit(self, X):
        X = StandardScaler().fit_transform(X)
        return self.clf.predict_proba(X)[:, 1], self.clf.predict(X)
