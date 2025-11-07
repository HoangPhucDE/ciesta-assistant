from typing import Any, Dict, List, Text
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.constants import ENTITIES
from rasa.shared.nlu.training_data.message import Message
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

@DefaultV1Recipe.register(
    component_name="EntityFilter",
    is_trainable=False
)
class EntityFilter(GraphComponent):
    """Custom component to filter out single-word entities that are common Vietnamese words."""
    
    def __init__(
        self,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
    ) -> None:
        """Initialize the component."""
        self.excluded_words = {
            "giới", "ẩm", "hãy", "xin", "địa",
            "cho", "về", "với", "và", "hay",
            "các", "những", "mọi", "một", "hai",
            "ba", "bốn", "năm", "sáu", "bảy",
            "tám", "chín", "mười"
        }

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        """Creates a new instance of the component."""
        return cls(config, model_storage, resource)

    def process(self, messages: List[Message]) -> List[Message]:
        """Process a list of messages and filter out unwanted entities."""
        for message in messages:
            if ENTITIES in message.data:
                filtered_entities = []
                for entity in message.get(ENTITIES):
                    # Get the actual text value from the message
                    entity_text = message.text[entity["start"]:entity["end"]].lower()
                    
                    # Only keep entities that are:
                    # 1. Not in excluded words list
                    # 2. Have more than one syllable (contains space)
                    # 3. Or are special abbreviations (like HCM)
                    if (entity_text not in self.excluded_words and 
                        (" " in entity_text or 
                         entity_text.upper() in {"HCM", "TPHCM", "TP"})):
                        filtered_entities.append(entity)
                
                message.set(ENTITIES, filtered_entities)
        
        return messages