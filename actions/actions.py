# FILE: actions/actions.py

import json
import os
import unicodedata
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# --- Hàm hỗ trợ chuẩn hóa tên file ---
def normalize_vietnamese_text(text: Text) -> Text:
    """
    Chuẩn hóa văn bản tiếng Việt để tạo tên file.
    Ví dụ: "Hà Nội" -> "ha_noi", "Đắk Lắk" -> "dak_lak"
    """
    if not text:
        return ""
    # Chuyển thành dạng không dấu và bỏ các ký tự đặc biệt
    no_accent_text = "".join(
        c for c in unicodedata.normalize("NFD", text) 
        if unicodedata.category(c) != "Mn"
    )
    # Xử lý chữ "Đ"
    no_accent_text = no_accent_text.replace("Đ", "D").replace("đ", "d")
    # Thay thế khoảng trắng bằng gạch dưới và chuyển thành chữ thường
    return no_accent_text.replace(" ", "_").lower()

# --- Action chính để tra cứu và trả lời ---
class ActionQueryKnowledgeBase(Action):

    def name(self) -> Text:
        # Tên của action này, phải trùng với tên trong domain.yml
        return "action_query_knowledge_base"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Lấy thông tin từ slot
        location = tracker.get_slot("location")
        requested_info = tracker.get_slot("requested_info")

        # Nếu không có địa điểm, yêu cầu người dùng cung cấp
        if not location:
            dispatcher.utter_message(response="utter_ask_for_location")
            return []

        try:
            # Xây dựng đường dẫn file dựa trên tên địa điểm đã chuẩn hóa
            normalized_location = normalize_vietnamese_text(location)
            file_path = os.path.join("data", "knowledge_base", "provinces", f"{normalized_location}.json")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Tìm đúng data của tỉnh trong file JSON
            # Chúng ta cần tìm key có tên trùng với `location`, ví dụ "Hà Nội"
            province_data = None
            for key in data:
                if key.lower() == location.lower():
                    province_data = data[key]
                    break
            
            if not province_data:
                dispatcher.utter_message(text=f"Xin lỗi, tôi chưa có dữ liệu chi tiết cho '{location}'.")
                return [SlotSet("location", None)]

            # Xây dựng câu trả lời dựa trên yêu cầu
            response_title = f"📝 Dưới đây là thông tin về **{location}**:"
            response_body = ""

            info_list = []
            if requested_info == "places_to_visit":
                response_title = f"🏞️ Các địa điểm không thể bỏ lỡ tại **{location}**:"
                info_list = province_data.get("places_to_visit", [])
            elif requested_info == "what_to_eat":
                response_title = f"🍜 Đặc sản ẩm thực tại **{location}**:"
                info_list = province_data.get("what_to_eat", [])
            elif requested_info == "festivals":
                response_title = f"🎊 Các lễ hội đặc sắc tại **{location}**:"
                info_list = province_data.get("festivals", [])
            else: # Trường hợp hỏi chung chung hoặc intent không khớp
                response_body = province_data.get("culture_details", "Tôi chưa có mô tả chi tiết.") + "\n\n"
                info_list = province_data.get("places_to_visit", []) # Gợi ý thêm vài địa điểm
                if info_list:
                    response_body += "Bạn có thể ghé thăm một vài nơi nổi bật như:\n"
            
            # Định dạng danh sách thông tin
            if info_list:
                for item in info_list:
                    item_name = item.get("name", "N/A")
                    item_details = item.get("details", "")
                    response_body += f"- **{item_name}**: {item_details}\n"

            # Gửi câu trả lời
            dispatcher.utter_message(text=f"{response_title}\n{response_body}")

        except FileNotFoundError:
            dispatcher.utter_message(text=f"Xin lỗi, tôi chưa có thông tin chi tiết về '{location}'. Tôi sẽ sớm cập nhật.")
        
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            dispatcher.utter_message(text="Rất tiếc, đã có lỗi xảy ra khi tôi tìm kiếm thông tin.")

        # Xóa các slot sau khi đã trả lời để chuẩn bị cho câu hỏi mới
        return [SlotSet("location", None), SlotSet("requested_info", None)]