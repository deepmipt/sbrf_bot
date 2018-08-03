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
from scipy.sparse import vstack
from scipy.sparse import csr_matrix

from deeppavlov.core.common.registry import register
from deeppavlov.core.common.log import get_logger
from deeppavlov.core.models.estimator import Estimator
from deeppavlov.core.common.file import save_pickle
from deeppavlov.core.common.file import load_pickle
from deeppavlov.core.commands.utils import expand_path
from deeppavlov.core.models.serializable import Serializable

logger = get_logger(__name__)


@register("faq_cos_model")
class FaqCosineSimilarityModel(Estimator, Serializable):

    def __init__(self, save_path: str = None, load_path: str = None, **kwargs) -> None:
        self.save_path = save_path
        self.load_path = load_path
        if kwargs['mode'] != 'train':
            self.load()

    def __call__(self, q_vect) -> List[str]:
        cos_similarities = np.array(q_vect[0].dot(self.x_train_features.T).todense())[0]
        answer_id = np.argmax(cos_similarities)
        answer, score, state = [self.y_train[answer_id]], [np.round(cos_similarities[answer_id], 2)], [None]
        logger.debug([answer, score])
        return answer, score, state

    def fit(self, x_train_vects, y_train) -> None:
        if len(x_train_vects) != 0:
            if isinstance(x_train_vects[0], csr_matrix):
                self.x_train_features = vstack(list(x_train_vects))
            else:
                raise NotImplementedError('Not implemented this type of vectors')
        else:
            raise ValueError("Train vectors can't be empty")

        self.y_train = list(y_train)


    def save(self) -> None:
        logger.info("Saving faq_model to {}".format(self.save_path))
        save_pickle((self.x_train_features,self.y_train), expand_path(self.save_path))


    def load(self) -> None:
        logger.info("Loading faq_model from {}".format(self.load_path))
        self.x_train_features, self.y_train = load_pickle(expand_path(self.load_path))
