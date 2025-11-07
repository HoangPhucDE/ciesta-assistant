"""
Custom component for Vietnamese text preprocessing with enhanced accuracy
"""
from typing import Any, Dict, List, Text, Type
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData
import regex as re
import unicodedata

@DefaultV1Recipe.register(
    component_types=[DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER],
    is_trainable=False
)
class VietnameseTextPreprocessor(GraphComponent):
    """Custom component for preprocessing Vietnamese text with improved accuracy"""
    
    @classmethod
    def required_components(cls) -> List[Type]:
        """No components required."""
        return []

    @classmethod
    def required_packages(cls) -> List[Text]:
        """No additional packages required."""
        return ["regex"]

    def __init__(
        self,
        config: Dict[Text, Any],
        name: Text,
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> None:
        """Initialize the preprocessor."""
        self._config = config
        self._name = name
        self._model_storage = model_storage
        self._resource = resource
        self._execution_context = execution_context
        self._initialize_mappings()

    def _initialize_mappings(self):
        """Initialize character and word mappings"""
        # Chuẩn hóa dấu tiếng Việt
        self.vietnamese_chars = {
            'òa': 'oà', 'óa': 'oá', 'ỏa': 'oả', 'õa': 'oã', 'ọa': 'oạ',
            'òe': 'oè', 'óe': 'oé', 'ỏe': 'oẻ', 'õe': 'oẽ', 'ọe': 'oẹ',
            'ùy': 'uỳ', 'úy': 'uý', 'ủy': 'uỷ', 'ũy': 'uỹ', 'ụy': 'uỵ',
            'Đ': 'đ',
            # Thêm các biến thể phổ biến
            'ă': 'ă', 'â': 'â', 'đ': 'đ', 'ê': 'ê', 'ô': 'ô', 'ơ': 'ơ', 'ư': 'ư',
            'á': 'á', 'à': 'à', 'ã': 'ã', 'ả': 'ả', 'ạ': 'ạ',
            'ắ': 'ắ', 'ằ': 'ằ', 'ẵ': 'ẵ', 'ẳ': 'ẳ', 'ặ': 'ặ',
            'ấ': 'ấ', 'ầ': 'ầ', 'ẫ': 'ẫ', 'ẩ': 'ẩ', 'ậ': 'ậ',
            'é': 'é', 'è': 'è', 'ẽ': 'ẽ', 'ẻ': 'ẻ', 'ẹ': 'ẹ',
            'ế': 'ế', 'ề': 'ề', 'ễ': 'ễ', 'ể': 'ể', 'ệ': 'ệ',
            'í': 'í', 'ì': 'ì', 'ĩ': 'ĩ', 'ỉ': 'ỉ', 'ị': 'ị',
            'ó': 'ó', 'ò': 'ò', 'õ': 'õ', 'ỏ': 'ỏ', 'ọ': 'ọ',
            'ố': 'ố', 'ồ': 'ồ', 'ỗ': 'ỗ', 'ổ': 'ổ', 'ộ': 'ộ',
            'ớ': 'ớ', 'ờ': 'ờ', 'ỡ': 'ỡ', 'ở': 'ở', 'ợ': 'ợ',
            'ú': 'ú', 'ù': 'ù', 'ũ': 'ũ', 'ủ': 'ủ', 'ụ': 'ụ',
            'ứ': 'ứ', 'ừ': 'ừ', 'ữ': 'ữ', 'ử': 'ử', 'ự': 'ự',
            'ý': 'ý', 'ỳ': 'ỳ', 'ỹ': 'ỹ', 'ỷ': 'ỷ', 'ỵ': 'ỵ'
        }

        # Từ viết tắt và biến thể
        self.abbreviations = {
            'tp': 'thành phố',
            'tp.': 'thành phố',
            't.p': 'thành phố',
            'q.': 'quận',
            'p.': 'phường',
            'kv': 'khu vực',
            'kv.': 'khu vực',
            'đc': 'địa chỉ',
            'sđt': 'số điện thoại',
            'đt': 'điện thoại'
        }

        # Lỗi chính tả phổ biến
        self.typo_map = {
            'di lich': 'du lịch',
            'di ljch': 'du lịch',
            'di ịch': 'du lịch',
            'am thuc': 'ẩm thực',
            'am thưc': 'ẩm thực',
            'van hoa': 'văn hoá',
            'van hóa': 'văn hoá',
            'le hoi': 'lễ hội',
            'le hôi': 'lễ hội',
            'dia diem': 'địa điểm',
            'dja diem': 'địa điểm',
            'đia điem': 'địa điểm',
            'quan an': 'quán ăn',
            'nha hang': 'nhà hàng',
            'khach san': 'khách sạn',
            'bai bien': 'bãi biển',
            'cho': 'chợ',
            'diem tham quan': 'điểm tham quan'
        }

    def _normalize_vietnamese_text(self, text: str) -> str:
        """Chuẩn hóa văn bản tiếng Việt"""
        # Chuẩn hóa dấu về dạng tổng hợp
        text = unicodedata.normalize('NFC', text)
        
        # Chuyển về chữ thường
        text = text.lower()
        
        # Xử lý các biến thể ký tự
        for old, new in self.vietnamese_chars.items():
            text = text.replace(old, new)
            
        # Xử lý từ viết tắt
        for abbr, full in self.abbreviations.items():
            text = re.sub(rf'\b{abbr}\b', full, text, flags=re.IGNORECASE)
            
        # Sửa lỗi chính tả
        for typo, correct in self.typo_map.items():
            text = re.sub(rf'\b{typo}\b', correct, text, flags=re.IGNORECASE)
        
        # Xử lý dấu câu và khoảng trắng
        text = re.sub(r'[^\w\s\đ\á\à\ã\ả\ạ\ắ\ằ\ẵ\ẳ\ặ\ấ\ầ\ẫ\ẩ\ậ\é\è\ẽ\ẻ\ẹ\ế\ề\ễ\ể\ệ\í\ì\ĩ\ỉ\ị\ó\ò\õ\ỏ\ọ\ố\ồ\ỗ\ổ\ộ\ớ\ờ\ỡ\ở\ợ\ú\ù\ũ\ủ\ụ\ứ\ừ\ữ\ử\ự\ý\ỳ\ỹ\ỷ\ỵ]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text

    def process(self, messages: List[Message]) -> List[Message]:
        """Process a list of messages."""
        for message in messages:
            if not message.get("text"):
                continue

            # Normalize text
            text = message.get("text")
            normalized_text = self._normalize_vietnamese_text(text)
            
            # Update message
            message.set("text", normalized_text, add_to_output=True)
            
            # Add original text as a feature for reference
            message.set("original_text", text)
            
        return messages

    def process_message(self, message: Message) -> Message:
        """Process a single message."""
        if message.get("text"):
            text = message.get("text")
            normalized_text = self._normalize_vietnamese_text(text)
            message.set("text", normalized_text, add_to_output=True)
            message.set("original_text", text)
        return message

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> GraphComponent:
        """Create a new component."""
        return cls(
            config=config,
            name=cls.__name__,
            model_storage=model_storage,
            resource=resource,
            execution_context=execution_context,
        )

    def train(self, training_data: TrainingData) -> Resource:
        """Process all training examples."""
        self.process_training_data(training_data)
        return self._resource
        
    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        """Process the training data."""
        self.process(training_data.training_examples)
        return training_data