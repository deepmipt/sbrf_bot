"""
Copyright 2017 Neural Networks and Deep Learning lab, MIPT
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy as np
from typing import List

from deeppavlov.core.common.registry import register
from deeppavlov.core.common.log import get_logger
from deeppavlov.core.models.estimator import Estimator
from deeppavlov.core.common.file import save_pickle
from deeppavlov.core.common.file import load_pickle
from deeppavlov.core.commands.utils import expand_path
from deeppavlov.core.models.serializable import Serializable

logger = get_logger(__name__)


@register("demo_clf")
class SbrfDemoClasiifier(Estimator, Serializable):

    def __init__(self, save_path: str = None, load_path: str = None, **kwargs) -> None:
        self.clf = None
        self.classes = ['FAQ', 'RATES', 'SMS_INFORM', 'OPEN_ACCOUNT', 'OTHER']
        super().__init__(save_path, load_path)
        self.load()

    def __call__(self, vector):
        answer = self.clf.predict(vector)[0]
        score = np.max(self.clf.predict_proba(vector))
        logger.debug([answer, score])
        return [self.classes[answer]], [score], [None]

    def fit(self, X, y) -> None:
        self.clf.fit(X, y)

    def save(self) -> None:
        logger.info("Saving classifier to {}".format(self.save_path))
        save_pickle(self.clf, expand_path(self.save_path))

    def load(self) -> None:
        logger.info("Loading classifier from {}".format(self.load_path))
        self.clf = load_pickle(expand_path(self.load_path))
