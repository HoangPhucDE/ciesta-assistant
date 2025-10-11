# FILE: actions/actions.py

import json
import os
import unicodedata
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# --- Global cache cho dữ liệu JSON để tối ưu hiệu suất ---
PROVINCE_DATA_CACHE = {}  # Lưu dữ liệu tất cả tỉnh, key là normalized_location

# --- Danh sách synonym cho tỉnh cũ/mới sau sáp nhập theo Nghị quyết 202/2025/QH15 ---
# Key: normalized tên tỉnh cũ bị gộp, Value: normalized tên tỉnh mới
SYNONYMS = {
    # Tỉnh Lào Cai mới (gộp Yên Bái, Lào Cai)
    "yen_bai": "lao_cai",

    # Tỉnh Thái Nguyên mới (gộp Bắc Kạn, Thái Nguyên)
    "bac_kan": "thai_nguyen",

    # Tỉnh Phú Thọ mới (gộp Vĩnh Phúc, Hòa Bình, Phú Thọ)
    "vinh_phuc": "phu_tho",
    "hoa_binh": "phu_tho",

    # Tỉnh Bắc Ninh mới (gộp Bắc Giang, Bắc Ninh)
    "bac_giang": "bac_ninh",

    # Tỉnh Hưng Yên mới (gộp Thái Bình, Hưng Yên)
    "thai_binh": "hung_yen",

    # Thành phố Hải Phòng mới (gộp Hải Phòng, Hải Dương)
    "hai_duong": "hai_phong",

    # Tỉnh Ninh Bình mới (gộp Hà Nam, Nam Định, Ninh Bình)
    "ha_nam": "ninh_binh",
    "nam_dinh": "ninh_binh",

    # Tỉnh Quảng Trị mới (gộp Quảng Bình, Quảng Trị)
    "quang_binh": "quang_tri",

    # Thành phố Đà Nẵng mới (gộp Đà Nẵng, Quảng Nam)
    "quang_nam": "da_nang",

    # Tỉnh Quảng Ngãi mới (gộp Kon Tum, Quảng Ngãi)
    "kon_tum": "quang_ngai",

    # Tỉnh Gia Lai mới (gộp Bình Định, Gia Lai)
    "binh_dinh": "gia_lai",

    # Tỉnh Khánh Hòa mới (gộp Ninh Thuận, Khánh Hòa)
    "ninh_thuan": "khanh_hoa",

    # Tỉnh Lâm Đồng mới (gộp Đắk Nông, Bình Thuận, Lâm Đồng)
    "dak_nong": "lam_dong",
    "binh_thuan": "lam_dong",

    # Tỉnh Đắk Lắk mới (gộp Phú Yên, Đắk Lắk)
    "phu_yen": "dak_lak",

    # Thành phố Hồ Chí Minh mới (gộp TP. Hồ Chí Minh, Bà Rịa - Vũng Tàu, Bình Dương)
    "ba_ria_vung_tau": "ho_chi_minh",
    "binh_duong": "ho_chi_minh",

    # Tỉnh Đồng Nai mới (gộp Bình Phước, Đồng Nai)
    "binh_phuoc": "dong_nai",

    # Tỉnh Tây Ninh mới (gộp Long An, Tây Ninh)
    "long_an": "tay_ninh",

    # Thành phố Cần Thơ mới (gộp Cần Thơ, Sóc Trăng, Hậu Giang)
    "soc_trang": "can_tho",
    "hau_giang": "can_tho",

    # Tỉnh Vĩnh Long mới (gộp Bến Tre, Trà Vinh, Vĩnh Long)
    "ben_tre": "vinh_long",
    "tra_vinh": "vinh_long",

    # Tỉnh Đồng Tháp mới (gộp Tiền Giang, Đồng Tháp)
    "tien_giang": "dong_thap",

    # Tỉnh Cà Mau mới (gộp Bạc Liêu, Cà Mau)
    "bac_lieu": "ca_mau",

    # Tỉnh An Giang mới (gộp Kiên Giang, An Giang)
    "kien_giang": "an_giang",

    # Các synonym khác cho tên gọi phổ biến hoặc biến thể (không sáp nhập nhưng để hỗ trợ)
    "kinh_bac": "bac_ninh",  # Biến thể cho Bắc Ninh
    "phu_quoc": "an_giang",  # Phú Quốc thuộc An Giang mới
    "chau_doc": "an_giang",  # Châu Đốc thuộc An Giang mới
    # Thêm biến thể nếu cần, ví dụ:
    "saigon": "ho_chi_minh",
    "hue": "hue"  # Giữ nguyên
}

def load_all_provinces():
    """Tải tất cả file JSON vào cache khi khởi động."""
    if PROVINCE_DATA_CACHE:
        return  # Đã tải rồi
    provinces_dir = os.path.join("data", "knowledge_base", "provinces")
    for filename in os.listdir(provinces_dir):
        if filename.endswith(".json"):
            normalized_location = filename.replace(".json", "")
            file_path = os.path.join(provinces_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            PROVINCE_DATA_CACHE[normalized_location] = data

# Tải cache ngay khi import file
load_all_provinces()

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
        time_filter = tracker.get_slot("time")  # Thêm slot time để lọc festival

        # Nếu không có địa điểm, yêu cầu người dùng cung cấp
        if not location:
            dispatcher.utter_message(response="utter_ask_for_location")
            return []

        try:
            # Xử lý synonym nếu có
            normalized_location = normalize_vietnamese_text(location)
            if normalized_location in SYNONYMS:
                normalized_location = SYNONYMS[normalized_location]

            # Lấy data từ cache
            data = PROVINCE_DATA_CACHE.get(normalized_location)
            if not data:
                dispatcher.utter_message(text=f"Xin lỗi, tôi chưa có dữ liệu cho '{location}'. Tôi sẽ sớm cập nhật.")
                return [SlotSet("location", None)]

            # Tìm đúng data của tỉnh trong JSON
            province_data = None
            for key in data:
                if normalize_vietnamese_text(key) == normalized_location:
                    province_data = data[key]
                    break
            
            if not province_data:
                dispatcher.utter_message(text=f"Xin lỗi, tôi chưa có dữ liệu chi tiết cho '{location}'.")
                return [SlotSet("location", None)]

            # Xử lý sub_regions nếu requested_info là "sub_regions" hoặc hỏi về sáp nhập
            if requested_info == "sub_regions" or "sap_nhap" in requested_info.lower() or "moi_gom" in requested_info.lower():
                response_title = f"🗺️ Cấu trúc vùng miền của **{location} mới**:"
                response_body = ""
                sub_regions = province_data.get("sub_regions", [])
                if sub_regions:
                    for region in sub_regions:
                        name = region.get("name", "N/A")
                        highlights = region.get("highlights", "")
                        response_body += f"- **{name}**: {highlights}\n"
                else:
                    response_body = "Tỉnh này không có dữ liệu về các khu vực con."
                dispatcher.utter_message(text=f"{response_title}\n{response_body}")
                return [SlotSet("location", None), SlotSet("requested_info", None)]

            # Xây dựng câu trả lời dựa trên requested_info
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
                festivals = province_data.get("festivals", [])
                if time_filter:
                    # Lọc festival theo time nếu có
                    filtered_festivals = [f for f in festivals if time_filter.lower() in f.get("time", "").lower()]
                    info_list = filtered_festivals if filtered_festivals else festivals
                    if filtered_festivals:
                        response_title += f" (lọc theo '{time_filter}')"
                    else:
                        response_body += f"Không tìm thấy lễ hội vào '{time_filter}', đây là tất cả lễ hội:\n"
                else:
                    info_list = festivals
            elif requested_info == "transportation":
                response_title = f"🚗 Phương tiện di chuyển đến **{location}**:"
                transportation = province_data.get("transportation", [])
                if transportation:
                    response_body = "\n".join([f"- {item}" for item in transportation])
                else:
                    response_body = "Chưa có dữ liệu về phương tiện di chuyển."
            else:  # Hỏi chung chung
                response_body = province_data.get("culture_details", "Tôi chưa có mô tả chi tiết.") + "\n\n"
                response_body += "Bạn có thể ghé thăm một vài nơi nổi bật như:\n"
                info_list = province_data.get("places_to_visit", [])[:3]  # Gợi ý 3 địa điểm đầu
                response_body += "\nNgoài ra, một số lễ hội đáng chú ý:\n"
                info_list += province_data.get("festivals", [])[:2]  # Gợi ý 2 lễ hội

            # Định dạng danh sách thông tin
            if info_list:
                for item in info_list:
                    item_name = item.get("name", "N/A")
                    item_details = item.get("details", "")
                    item_time = item.get("time", "")  # Nếu là festival
                    response_body += f"- **{item_name}** ({item_time}): {item_details}\n"

            # Gửi câu trả lời
            dispatcher.utter_message(text=f"{response_title}\n{response_body}")

        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")
            dispatcher.utter_message(text="Rất tiếc, đã có lỗi xảy ra khi tôi tìm kiếm thông tin.")

        # Xóa các slot sau khi đã trả lời để chuẩn bị cho câu hỏi mới
        return [SlotSet("location", None), SlotSet("requested_info", None), SlotSet("time", None)]