from typing import Any, Dict, List, Optional, Text
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.features import Features

from transformers import AutoTokenizer, AutoModel
import numpy as np
import torch

@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=False
)
class PhoBERTFeaturizer(GraphComponent):
    """Custom Featurizer sử dụng PhoBERT để sinh dense features cho Rasa."""

    @classmethod
    def required_packages(cls) -> List[Text]:
        return ["transformers", "torch", "numpy"]

    def __init__(
        self,
        config: Dict[Text, Any],
        name: Text,
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> None:
        self.name = name
        self.config = config
        self.model_storage = model_storage
        self.resource = resource
        self.execution_context = execution_context

        self.model_name = config.get("model_name", "vinai/phobert-base")
        self.cache_dir = config.get("cache_dir", None)
        self.max_length = config.get("max_length", 256)
        self.pooling_strategy = config.get("pooling_strategy", "mean_max")  # "mean", "max", "mean_max"

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        print(f"[PhoBERTFeaturizer] 🔹 Loading model from: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, 
            cache_dir=self.cache_dir,
            use_fast=True  # Use fast tokenizer
        )
        self.model = AutoModel.from_pretrained(
            self.model_name,
            cache_dir=self.cache_dir,
            output_hidden_states=True,  # Get all hidden states
            output_attentions=True,     # Get attention weights
            return_dict=True
        ).to(self.device)
        self.model.eval()
        
        # Set hidden size based on pooling strategy
        base_hidden_size = getattr(getattr(self.model, "config", None), "hidden_size", 1024)
        if self.pooling_strategy == "mean_max":
            # Double hidden size since we concatenate mean and max pooling
            self.hidden_size = 2 * base_hidden_size
        else:
            # Single hidden size for mean or max only
            self.hidden_size = base_hidden_size

    # Rasa sẽ gọi hàm create() khi load pipeline
    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "PhoBERTFeaturizer":
        return cls(config, cls.__name__, model_storage, resource, execution_context)

    def _get_text_embeddings(self, text: Text) -> np.ndarray:
        if not text:
            # Trả về vector zeros đúng kích thước ẩn của model
            return np.zeros((1, self.hidden_size))

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length,
            add_special_tokens=True,
            return_attention_mask=True,
            return_token_type_ids=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            
            # Get attention mask
            attention_mask = inputs['attention_mask']
            
            # Get last hidden state
            last_hidden = outputs[0]
            
            # Apply attention mask
            mask = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
            masked_embeddings = last_hidden * mask
            
            # Pooling based on strategy
            if self.pooling_strategy == "mean":
                # Mean pooling only
                summed = torch.sum(masked_embeddings, dim=1)
                counted = torch.clamp(mask.sum(dim=1), min=1e-9)
                pooled = summed / counted
            elif self.pooling_strategy == "max":
                # Max pooling only
                pooled = torch.max(masked_embeddings, dim=1)[0]
            else:  # "mean_max" or default
                # Mean pooling
                summed = torch.sum(masked_embeddings, dim=1)
                counted = torch.clamp(mask.sum(dim=1), min=1e-9)
                mean_pooled = summed / counted
                
                # Max pooling
                max_pooled = torch.max(masked_embeddings, dim=1)[0]
                
                # Concatenate mean and max pooling
                pooled = torch.cat([mean_pooled, max_pooled], dim=-1)
            
            # Convert to numpy
            embeddings = pooled.cpu().numpy()

        return embeddings

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            text = message.get("text")
            if text:
                emb = self._get_text_embeddings(text)
                message.add_features(
                    Features(
                        emb,
                        attribute="text",
                        feature_type="dense",
                        origin=self.__class__.__name__,
                    )
                )
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        self.process(training_data.training_examples)
        return training_data