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
import os
from pathlib import Path

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
        self.batch_size = config.get("batch_size", 32)  # Batch size for processing multiple texts

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Log device info for debugging
        if torch.cuda.is_available():
            print(f"[PhoBERTFeaturizer] ✅ GPU detected: {torch.cuda.get_device_name(0)}")
            print(f"[PhoBERTFeaturizer] ✅ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            print(f"[PhoBERTFeaturizer] ⚠️  No GPU detected - Using CPU (training will be slower)")
            print(f"[PhoBERTFeaturizer] 💡 Tip: Install CUDA and PyTorch with GPU support for faster training")

        # Resolve local model path if it's a relative path
        # Check if model_name is a local path (not a HuggingFace model ID)
        is_local_path = False
        if not self.model_name.startswith(("http://", "https://")) and "/" in self.model_name:
            model_path = Path(self.model_name)
            
            # Try to resolve the path
            if model_path.is_absolute():
                # Absolute path - check if exists
                if model_path.exists():
                    self.model_name = str(model_path.resolve())
                    is_local_path = True
            else:
                # Relative path - try multiple locations
                # 1. Try relative to current working directory
                abs_path = Path.cwd() / model_path
                if abs_path.exists():
                    self.model_name = str(abs_path.resolve())
                    is_local_path = True
                else:
                    # 2. Try relative to workspace root (where config.yml is)
                    workspace_root = Path(__file__).parent.parent
                    abs_path = workspace_root / model_path
                    if abs_path.exists():
                        self.model_name = str(abs_path.resolve())
                        is_local_path = True

        print(f"[PhoBERTFeaturizer] 🔹 Loading model from: {self.model_name}")
        print(f"[PhoBERTFeaturizer] 🔹 Using device: {self.device}")
        print(f"[PhoBERTFeaturizer] 🔹 Local model: {is_local_path}")
        
        # For local paths, don't use cache_dir
        load_cache_dir = None if is_local_path else self.cache_dir
        
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, 
            cache_dir=load_cache_dir,
            use_fast=True,  # Use fast tokenizer
            local_files_only=is_local_path  # Use local files only if path exists
        )
        self.model = AutoModel.from_pretrained(
            self.model_name,
            cache_dir=load_cache_dir,
            output_hidden_states=True,  # Get all hidden states
            output_attentions=True,     # Get attention weights
            return_dict=True,
            local_files_only=is_local_path  # Use local files only if path exists
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
        """Process a single text (kept for backward compatibility)."""
        if not text:
            return np.zeros((1, self.hidden_size))
        embeddings = self._get_batch_embeddings([text])
        return embeddings[0:1]  # Return first embedding as (1, hidden_size)
    
    def _get_batch_embeddings(self, texts: List[Text]) -> np.ndarray:
        """Process a batch of texts efficiently."""
        if not texts:
            return np.zeros((0, self.hidden_size))
        
        # Filter out empty texts and keep track of indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            # All texts are empty
            return np.zeros((len(texts), self.hidden_size))
        
        # Tokenize all texts at once (much faster)
        inputs = self.tokenizer(
            valid_texts,
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
            last_hidden = outputs[0]  # Shape: (batch_size, seq_len, hidden_size)
            
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
            valid_embeddings = pooled.cpu().numpy()
        
        # Create output array for all texts (including empty ones)
        if len(valid_texts) == len(texts):
            return valid_embeddings
        else:
            # Some texts were empty, need to fill in zeros
            embeddings = np.zeros((len(texts), self.hidden_size))
            for idx, valid_idx in enumerate(valid_indices):
                embeddings[valid_idx] = valid_embeddings[idx]
            return embeddings

    def process(self, messages: List[Message]) -> List[Message]:
        """Process messages in batches for better performance."""
        if not messages:
            return messages
        
        # Extract all texts
        texts = [message.get("text") or "" for message in messages]
        
        # Process in batches to avoid memory issues
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self._get_batch_embeddings(batch_texts)
            all_embeddings.append(batch_embeddings)
        
        # Concatenate all batches
        if all_embeddings:
            embeddings = np.vstack(all_embeddings)
        else:
            embeddings = np.zeros((len(messages), self.hidden_size))
        
        # Add features to messages
        for message, emb in zip(messages, embeddings):
            # Reshape to (1, hidden_size) for Rasa
            message.add_features(
                Features(
                    emb.reshape(1, -1),
                    attribute="text",
                    feature_type="dense",
                    origin=self.__class__.__name__,
                )
            )
        
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        self.process(training_data.training_examples)
        return training_data