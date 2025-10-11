from typing import Dict, Text, Any, List, Optional
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.features import Features

from transformers import AutoModel, AutoTokenizer
import torch
import numpy as np


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=False
)
class PhoBERTFeaturizer(GraphComponent):
    """
    Custom Featurizer sử dụng PhoBERT để tạo dense features cho văn bản trong Rasa NLU.
    """

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["transformers", "torch", "numpy"]

    def __init__(self, config: Dict[Text, Any], execution_context: ExecutionContext) -> None:
        self.config = config
        self.execution_context = execution_context

        self.model_name = config.get("model_name", "vinai/phobert-base")
        self.cache_dir = config.get("cache_dir", None)

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        self.model = AutoModel.from_pretrained(self.model_name, cache_dir=self.cache_dir)
        self.model.eval()

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: Any,
        resource: Optional[Any],
        execution_context: ExecutionContext
    ) -> "PhoBERTFeaturizer":
        return cls(config, execution_context)

    def _get_text_embeddings(self, text: Text) -> np.ndarray:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

        return np.expand_dims(embeddings, axis=0)

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            text = message.get("text")
            if text:
                feature_vector = self._get_text_embeddings(text)
                message.add_features(
                    Features(
                        feature_vector,
                        attribute="text",        
                        feature_type="dense",
                        origin=self.__class__.__name__,
                    )
                )
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        self.process(training_data.training_examples)
        return training_data
