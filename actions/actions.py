"""
FILE: actions.py
Custom actions để truy vấn knowledge base về các tỉnh thành Việt Nam
"""

import json
import os
import logging
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Load .env từ thư mục gốc của project
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logging.info(f"[Actions] Loaded .env from {env_path}")
    else:
        # Thử load từ thư mục hiện tại
        load_dotenv()
        logging.info("[Actions] Loaded .env from current directory")
except ImportError:
    logging.warning("[Actions] python-dotenv not installed, using system env vars only")
except Exception as e:
    logging.warning(f"[Actions] Failed to load .env: {e}")

# RAG imports
try:
    from rag.retriever import RAGRetriever
except Exception:
    RAGRetriever = None

class ActionQueryKnowledgeBase(Action):
    """
    Action tùy chỉnh để truy vấn knowledge base về du lịch Việt Nam
    """
    
    def __init__(self):
        super().__init__()
        self.knowledge_base = self._load_knowledge_base()
        # load raw mapping and build a lowercase-key mapping for case-insensitive lookup
        self.location_map_raw = self._load_location_map()
        self.location_map = {k.strip().lower(): v for k, v in self.location_map_raw.items()}

    def _load_location_map(self) -> Dict[str, str]:
        """Load location alias mapping from data/location_map.json"""
        map_path = os.path.join("data", "location_map.json")
        if not os.path.exists(map_path):
            print(f"Warning: Location map file {map_path} not found!")
            return {}
        try:
            with open(map_path, "r", encoding="utf-8") as f:
                location_map = json.load(f)
            return location_map
        except Exception as e:
            print(f"Error loading location map: {e}")
            return {}
    
    def _load_knowledge_base(self) -> Dict:
        """Load tất cả các file JSON từ thư mục data/knowledge_base/provinces"""
        knowledge_base = {}
        kb_dir = "data/knowledge_base/provinces"
        
        if not os.path.exists(kb_dir):
            print(f"Warning: Directory {kb_dir} not found!")
            return knowledge_base
        
        # Đọc tất cả file .json trong thư mục
        for filename in os.listdir(kb_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(kb_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        knowledge_base.update(data)
                    print(f"Loaded: {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        print(f"Total provinces loaded: {len(knowledge_base)}")
        return knowledge_base
    
    def name(self) -> Text:
        return "action_query_knowledge_base"
    
    def _normalize_location(self, location: str) -> str:
        """Chuẩn hóa tên địa điểm theo 34 tỉnh thành mới (Nghị quyết 12/6/2025)"""
        # Preserve original spacing, perform case-insensitive lookup
        location = location.strip()
        key = location.lower()
        return self.location_map.get(key, location)
    
    def _format_response(self, province_data: Dict, intent: str) -> str:
        """Format phản hồi dựa trên intent"""
        province_name = list(province_data.keys())[0]
        data = province_data[province_name]
        
        if intent == "ask_culture":
            response = f"📍 **{province_name}**\n\n"
            response += f"{data.get('culture_details', 'Không có thông tin văn hóa.')}\n\n"
            
            if 'sub_regions' in data and data['sub_regions']:
                response += "**Các khu vực đặc trưng:**\n"
                for region in data['sub_regions']:
                    response += f"• {region['name']}: {region['highlights']}\n"
            
            return response
        
        elif intent == "ask_attractions":
            response = f"📍 **Địa điểm tham quan tại {province_name}**\n\n"
            
            if 'places_to_visit' in data and data['places_to_visit']:
                for i, place in enumerate(data['places_to_visit'][:6], 1):
                    category = place.get('category', 'du lịch')
                    response += f"{i}. **{place['name']}** ({category})\n"
                    response += f"   {place['details']}\n\n"
            else:
                response += "Không có thông tin địa điểm tham quan."
            
            return response
        
        elif intent == "ask_cuisine":
            response = f"🍜 **Ẩm thực {province_name}**\n\n"
            
            if 'what_to_eat' in data and data['what_to_eat']:
                for i, food in enumerate(data['what_to_eat'], 1):
                    response += f"{i}. **{food['name']}**\n"
                    response += f"   {food['details']}\n\n"
            else:
                response += "Không có thông tin ẩm thực."
            
            if 'specialties_as_gifts' in data and data['specialties_as_gifts']:
                response += "\n**Đặc sản mua về:**\n"
                for gift in data['specialties_as_gifts']:
                    response += f"• {gift}\n"
            
            return response
        
        elif intent == "ask_festival":
            response = f"🎊 **Lễ hội tại {province_name}**\n\n"
            
            if 'festivals' in data and data['festivals']:
                for fest in data['festivals']:
                    response += f"**{fest['name']}**\n"
                    response += f"⏰ Thời gian: {fest['time']}\n"
                    response += f"{fest['details']}\n\n"
            else:
                response += "Không có thông tin lễ hội."
            
            return response
        
        elif intent == "ask_travel_tips":
            response = f"💡 **Mẹo du lịch {province_name}**\n\n"
            
            if 'best_time_to_visit' in data:
                response += f"**Thời điểm đẹp nhất:**\n{data['best_time_to_visit']}\n\n"
            
            if 'travel_tips' in data:
                response += f"**Lưu ý:**\n{data['travel_tips']}\n"
            
            return response
        
        elif intent == "ask_new_province":
            response = f"📋 **Cấu trúc tỉnh {province_name} sau sáp nhập**\n\n"
            
            if 'sub_regions' in data and data['sub_regions']:
                response += f"{province_name} bao gồm:\n"
                for region in data['sub_regions']:
                    response += f"• {region['name']}\n"
                response += f"\n{data.get('culture_details', '')}"
            else:
                response += "Không có thông tin sáp nhập."
            
            return response
        
        elif intent == "ask_transportation":
            response = f"🚗 **Phương tiện di chuyển đến {province_name}**\n\n"
            
            if 'transportation' in data:
                response += data['transportation']
            else:
                response += "Không có thông tin phương tiện di chuyển."
            
            return response
        
        else:
            # Trả về thông tin tổng quan
            response = f"📍 **{province_name}**\n\n"
            response += f"{data.get('culture_details', '')}\n\n"
            
            if 'best_time_to_visit' in data:
                response += f"**Thời điểm đẹp:** {data['best_time_to_visit']}"
            
            return response
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        
        # Lấy location entity
        location = None
        entities = tracker.latest_message.get('entities', [])
        for entity in entities:
            if entity.get('entity') == 'location':
                location = entity.get('value')
                break
        
        if not location:
            dispatcher.utter_message(
                text="Bạn muốn biết thông tin về tỉnh/thành phố nào? "
                     "Ví dụ: Bắc Ninh, An Giang, Hà Nội..."
            )
            return []
        
        # Chuẩn hóa tên địa điểm
        location = self._normalize_location(location)
        
        # Tìm trong knowledge base
        province_data = None
        for province_name, data in self.knowledge_base.items():
            if province_name.lower() == location.lower():
                province_data = {province_name: data}
                break
        
        if not province_data:
            dispatcher.utter_message(
                text=f"Xin lỗi, tôi chưa có thông tin về '{location}'. "
                     f"Hiện tôi có dữ liệu về {len(self.knowledge_base)} tỉnh thành. "
                     f"Bạn có thể hỏi về: {', '.join(list(self.knowledge_base.keys())[:5])}..."
            )
            return []
        
        # Lấy intent
        intent = tracker.latest_message.get('intent', {}).get('name', 'ask_culture')
        
        # Fallback: Detect intent từ message text nếu intent bị nhầm
        user_msg = (tracker.latest_message.get("text", "") or "").lower()
        if intent == "ask_transportation" and any(keyword in user_msg for keyword in ["ẩm thực", "ăn", "món", "đặc sản", "quán", "nhà hàng"]):
            # Nếu intent là transportation nhưng message có từ khóa ẩm thực, chuyển sang cuisine
            intent = "ask_cuisine"
        elif intent == "ask_cuisine" and any(keyword in user_msg for keyword in ["phương tiện", "đi bằng", "xe", "máy bay", "tàu", "di chuyển"]):
            # Nếu intent là cuisine nhưng message có từ khóa phương tiện, chuyển sang transportation
            intent = "ask_transportation"
        elif intent == "ask_transportation" and any(keyword in user_msg for keyword in ["địa điểm", "tham quan", "du lịch", "đi đâu", "check in"]):
            # Nếu intent là transportation nhưng message có từ khóa địa điểm, chuyển sang attractions
            intent = "ask_attractions"
        elif intent == "ask_attractions" and any(keyword in user_msg for keyword in ["phương tiện", "đi bằng", "xe", "máy bay", "tàu", "di chuyển"]):
            # Nếu intent là attractions nhưng message có từ khóa phương tiện, chuyển sang transportation
            intent = "ask_transportation"
        
        # Format và gửi phản hồi
        response = self._format_response(province_data, intent)
        dispatcher.utter_message(text=response)
        
        return [SlotSet("location", location)]


class ActionDefaultFallback(Action):
    """Action fallback khi bot không hiểu"""
    
    def name(self) -> Text:
        return "action_default_fallback"
    
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # First: quick attempt to detect a location alias in the raw message and answer from KB
        user_msg = (tracker.latest_message.get("text", "") or "").strip()
        try:
            normalizer = ActionQueryKnowledgeBase()
            low_msg = user_msg.lower()
            for alias in sorted(normalizer.location_map_raw.keys(), key=lambda x: -len(x)):
                if alias.lower() in low_msg:
                    canon = normalizer.location_map_raw.get(alias)
                    # find province data
                    province_data = None
                    for pname, data in normalizer.knowledge_base.items():
                        if pname.lower() == (canon or '').lower():
                            province_data = {pname: data}
                            break
                    if province_data:
                        # default to culture intent
                        response = normalizer._format_response(province_data, 'ask_culture')
                        dispatcher.utter_message(text=response)
                        return [SlotSet('location', canon)]
        except Exception as e:
            logging.getLogger(__name__).debug("DefaultFallback quick KB lookup failed: %s", e)

        message = (
            "Xin lỗi, tôi chưa hiểu rõ ý bạn. "
            "Bạn có thể hỏi tôi về:\n\n"
            "• Văn hóa các tỉnh thành\n"
            "• Địa điểm du lịch\n"
            "• Ẩm thực đặc sản\n"
            "• Lễ hội truyền thống\n"
            "• Phương tiện di chuyển\n"
            "• Mẹo du lịch\n"
            "• Thông tin về các tỉnh sau sáp nhập\n\n"
            "Ví dụ: 'Giới thiệu về Bắc Ninh' hoặc 'Đà Nẵng có địa điểm nào đẹp?'"
        )

        dispatcher.utter_message(text=message)
        return []

class ActionRAGFallback(Action):
    """Fallback RAG: dùng FAISS + (tùy chọn) LLM khi out_of_scope/nlu_fallback

    Behavior changes applied:
    - Only run when intent is explicitly 'out_of_scope' or 'nlu_fallback'
    - Short/greeting queries are ignored (ask user to clarify)
    - Use a confidence threshold (env RAG_CONFIDENCE_THRESHOLD or 0.55)
    """

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        kb_dir = os.path.join(os.getcwd(), "data/knowledge_base/provinces")
        self.retriever = None
        self.confidence_threshold = float(os.getenv("RAG_CONFIDENCE_THRESHOLD", "0.55"))
        # Load location_map from JSON for normalization
        map_path = os.path.join("data", "location_map.json")
        if os.path.exists(map_path):
            try:
                with open(map_path, "r", encoding="utf-8") as f:
                    self.location_map = json.load(f)
            except Exception as e:
                self.logger.warning(f"Error loading location map: {e}")
                self.location_map = {}
        else:
            self.logger.warning(f"Location map file {map_path} not found!")
            self.location_map = {}
        if RAGRetriever is not None:
            try:
                self.retriever = RAGRetriever(kb_dir=kb_dir)
            except Exception as e:
                self.logger.exception("[RAG] Could not initialize retriever: %s", e)

    def name(self) -> Text:
        return "action_rag_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        user_msg = (tracker.latest_message.get("text", "") or "").strip()
        intent = tracker.latest_message.get("intent", {}).get("name")

        # Debug: log invocation details to make tracing easier during tests
        self.logger.debug("[RAG_FALLBACK] invoked; intent=%s user_msg='%s' retriever_present=%s", intent, user_msg, bool(self.retriever))

        # Quick check: Detect greet/goodbye from message text if intent was misclassified
        user_msg_lower = user_msg.lower()
        greet_keywords = ["xin chào", "chào", "hello", "hi", "hey", "chào bạn", "chào bot", "chào ciesta"]
        goodbye_keywords = ["tạm biệt", "bye", "goodbye", "hẹn gặp lại", "cảm ơn", "thôi", "dừng lại", "kết thúc"]
        bot_challenge_keywords = ["bạn là ai", "bạn là gì", "bạn là bot", "bạn là người", "tên bạn", "giới thiệu về bạn"]
        
        if any(keyword in user_msg_lower for keyword in greet_keywords) and len(user_msg.split()) <= 3:
            # Likely a greeting that was misclassified
            dispatcher.utter_message(text="Xin chào! Tôi là Ciesta, bot giới thiệu văn hóa và du lịch các tỉnh thành Việt Nam. Bạn muốn biết gì hôm nay?")
            return []
        
        if any(keyword in user_msg_lower for keyword in goodbye_keywords) and len(user_msg.split()) <= 4:
            # Likely a goodbye that was misclassified
            dispatcher.utter_message(text="Tạm biệt! Hẹn gặp lại bạn trong hành trình khám phá Việt Nam.")
            return []
        
        if any(keyword in user_msg_lower for keyword in bot_challenge_keywords):
            # Likely a bot challenge that was misclassified
            dispatcher.utter_message(text="Tôi là Ciesta, bot du lịch được xây dựng bằng Rasa để giúp bạn khám phá văn hóa và du lịch các tỉnh thành Việt Nam!")
            return []

        # Quick path: if the raw message contains a known location alias, prefer the KB
        try:
            normalizer = ActionQueryKnowledgeBase()
            low_msg = (user_msg or "").lower()
            for alias in sorted(self.location_map.keys(), key=lambda x: -len(x)):
                if alias.lower() in low_msg:
                    canon = self.location_map.get(alias)
                    # find province data
                    province_data = None
                    for pname, data in normalizer.knowledge_base.items():
                        if pname.lower() == (canon or '').lower():
                            province_data = {pname: data}
                            break
                    if province_data:
                        # simple intent heuristics from text
                        t = low_msg
                        if 'ẩm thực' in t or 'ăn' in t:
                            intent_req = 'ask_cuisine'
                        elif 'địa điểm' in t or 'điểm' in t or 'tham quan' in t or 'đi ' in t:
                            intent_req = 'ask_attractions'
                        elif 'lễ hội' in t or 'lễ' in t:
                            intent_req = 'ask_festival'
                        elif 'mẹo' in t or 'lưu ý' in t:
                            intent_req = 'ask_travel_tips'
                        else:
                            intent_req = 'ask_culture'

                        response = normalizer._format_response(province_data, intent_req)
                        dispatcher.utter_message(text=response)
                        return [SlotSet('location', canon)]
        except Exception as e:
            self.logger.debug('KB quick-detect failed: %s', e)

        # Only trigger RAG for explicit fallback/out_of_scope intents
        allowed_intents = {"out_of_scope", "nlu_fallback"}
        if intent not in allowed_intents:
            self.logger.debug("ActionRAGFallback called for intent '%s' — skipping RAG", intent)
            return []


        # === Tối ưu: Chuẩn hóa alias tỉnh/thành trong truy vấn ===
        def normalize_location_in_text(text, tracker):
            try:
                # 1. Ưu tiên entity location nếu có
                entities = tracker.latest_message.get('entities', [])
                found = False
                for entity in entities:
                    if entity.get('entity') == 'location':
                        raw_loc = entity.get('value')
                        norm_loc = self.location_map.get(raw_loc.strip().title(), raw_loc)
                        if raw_loc != norm_loc and raw_loc in text:
                            text = text.replace(raw_loc, norm_loc)
                            found = True
                if found:
                    return text
                # 2. Nếu không có entity, thử match alias trong mapping (ưu tiên cụm dài)
                for alias in sorted(self.location_map.keys(), key=lambda x: -len(x)):
                    if alias in text:
                        text = text.replace(alias, self.location_map[alias])
                        break
                return text
            except Exception as e:
                self.logger.warning(f"Location normalization failed: {e}")
                return text

        norm_msg = normalize_location_in_text(user_msg, tracker)

        # Short/greeting queries should ask user to clarify instead of calling RAG
        if not norm_msg or len(norm_msg.split()) < 2:
            dispatcher.utter_message(text="Bạn có thể hỏi rõ hơn, ví dụ: 'Địa điểm du lịch Hồ Chí Minh', 'Ẩm thực Bắc Ninh', 'Lễ hội ở Huế'...")
            return []

        if not self.retriever:
            dispatcher.utter_message(
                text=(
                    "Xin lỗi, hiện chưa kích hoạt RAG. Vui lòng hỏi về văn hóa, địa điểm, ẩm thực, lễ hội, mẹo du lịch hoặc tỉnh sau sáp nhập."
                )
            )
            return []

        results = self.retriever.search(norm_msg, top_k=5)
        if not results:
            dispatcher.utter_message(text="Xin lỗi, tôi chưa có dữ liệu phù hợp để trả lời.")
            return []

        top_score = results[0][0]
        self.logger.debug("RAG top score: %s for query: %s", top_score, norm_msg)

        if top_score < self.confidence_threshold:
            dispatcher.utter_message(
                text=(
                    "Xin lỗi, tôi chưa chắc chắn câu trả lời. Bạn có thể hỏi cụ thể hơn về tỉnh/thành nào hoặc chủ đề nào không? Ví dụ: 'Ẩm thực Đà Nẵng', 'Lễ hội ở Huế', 'Địa điểm du lịch Vĩnh Long'..."
                )
            )
            return []

        # Nếu đủ confidence, tổng hợp (LLM optional) và trả về
        try:
            # Debug: log LLM provider và API key status
            provider = os.getenv("LLM_PROVIDER", "openai")
            api_key_set = bool(os.getenv("GROQ_API_KEY") or os.getenv("OPENAI_API_KEY") or 
                              os.getenv("HUGGINGFACE_API_KEY") or os.getenv("TOGETHER_API_KEY") or
                              os.getenv("GOOGLE_API_KEY"))
            self.logger.info(f"[RAG] Provider: {provider}, API key set: {api_key_set}")
            
            answer = self.retriever.synthesize(norm_msg, results)
            dispatcher.utter_message(text=answer)
        except Exception as e:
            self.logger.exception("RAG synthesis failed: %s", e)
            # Fallback message với thông tin debug
            error_msg = "Xin lỗi, xảy ra lỗi khi tổng hợp câu trả lời."
            if "API" in str(e) or "key" in str(e).lower():
                error_msg += "\n\n💡 Kiểm tra:\n• API key có đúng trong .env?\n• LLM_PROVIDER có đúng không?\n• Đã restart action server sau khi thêm .env?"
            dispatcher.utter_message(text=error_msg)

        return []