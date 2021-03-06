from dedupe.base import BaseBlocker, BaseDistance, BaseTrain, BaseCluster
from dedupe.block.blockers import TestBlocker
from dedupe.train.threshold import Threshold
from dedupe.distance.string import AllJaro
from dedupe.cluster.cluster import ConnectedComponents

from abc import ABCMeta, abstractmethod
from typing import List, Optional, Tuple
from dataclasses import dataclass
import pandas as pd
import numpy as np
import ray
import logging
root = logging.getLogger()
root.setLevel(logging.DEBUG)

@dataclass
class BaseModel(metaclass=ABCMeta):
    """ Abstract base class from which all model classes inherit.
    All descendent classes must implement predict, train, and candidates methods.
    """
    df: pd.DataFrame
    df2: Optional[pd.DataFrame] = None
    attributes: Optional[List[str]] = None
    attributes2: Optional[List[str]] = None
    blocker: Optional[BaseBlocker] = TestBlocker()
    distance: Optional[BaseDistance] = AllJaro()
    trainer: Optional[BaseTrain] = Threshold(threshold=0.85)
    cluster: Optional[BaseCluster] = ConnectedComponents()
    fp: str = "/home/csong/cs_github/deduper/cache"
    cpus: int = 1

    @abstractmethod
    def predict(self):
        return

    @abstractmethod    
    def fit(self):
        return

    @abstractmethod
    def _get_candidates(self):
        return


@dataclass
class Dedupe(BaseModel):
    """General dedupe block, inherits from BaseModel.
    """

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = self.df.columns
        if (self.cpus > 1) & (not ray.is_initialized()):
            ray.init(num_cpus=self.cpus)

    def predict(self) -> pd.DataFrame:
        """get clusters of matches and return cluster IDs"""

        idxmat, scores, y = self.fit()

        logging.info("get clusters")
        return self.cluster.get_df_cluster(
            matches=idxmat[y == 1].astype(int), 
            scores=scores[y == 1],
            rl=False
        )

    def fit(self) -> Tuple[np.array, np.array, np.array]:
        """learn p(match)"""

        idxmat = self._get_candidates()

        logging.info("get distance matrix")
        X = self.distance.get_distmat(self.df, self.df2, self.attributes, self.attributes2, idxmat)

        logging.info("learning")
        self.trainer.learn(self.df, X, idxmat, self.attributes)

        logging.info("make predictions")
        scores, y = self.trainer.fit(X)

        return idxmat, scores, y

    def _get_candidates(self) -> np.array:
        """get candidate pairs"""
        
        logging.info("get block maps")
        block_maps = self.blocker.get_block_maps(df=self.df, attributes=self.attributes)

        logging.info("get candidate pairs")
        return self.blocker.dedupe_get_candidates(
            block_maps
        )


@dataclass
class RecordLinkage(Dedupe, BaseModel):
    """General record linkage block, inherits from BaseModel.
    """

    def __post_init__(self):
        if (self.attributes is None) & (self.attributes2 is None):
            unq_cols = list(set(self.df.columns).intersection(self.df2.columns))
            self.attributes = self.attributes2 = unq_cols
        elif self.attributes2 is None:
            self.attributes2 = self.attributes

    def predict(self) -> pd.DataFrame:
        """get clusters of matches and return cluster IDs"""

        idxmat, scores, y = self.fit()
        return self.cluster.get_df_cluster(
            matches=idxmat[y == 1].astype(int), 
            scores=scores[y == 1],
            rl=True
        )

    def _get_candidates(self) -> np.array:
        "get candidate pairs"

        block_maps1, block_maps2 = [
            self.blocker.get_block_maps(df=_, attributes=self.attributes)
            for _ in [self.df, self.df2]
        ]

        return self.blocker.rl_get_candidates(
            block_maps1, block_maps2
        )
