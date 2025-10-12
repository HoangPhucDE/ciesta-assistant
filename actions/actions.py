"""
FILE: actions.py
Custom actions để truy vấn knowledge base về các tỉnh thành Việt Nam
"""

import json
import os
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionQueryKnowledgeBase(Action):
    """
    Action tùy chỉnh để truy vấn knowledge base về du lịch Việt Nam
    """
    
    def __init__(self):
        super().__init__()
        self.knowledge_base = self._load_knowledge_base()
    
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
        # Loại bỏ khoảng trắng thừa và viết hoa chữ cái đầu
        location = location.strip().title()
        
        # Map các tên khác nhau về tên chính theo 34 tỉnh thành mới
        location_map = {
            # === TP. HỒ CHÍ MINH (sáp nhập Bình Dương, Bà Rịa Vũng Tàu) ===
            "Sài Gòn": "Hồ Chí Minh",
            "Sai Gon": "Hồ Chí Minh",
            "HCM": "Hồ Chí Minh",
            "TP.HCM": "Hồ Chí Minh",
            "TPHCM": "Hồ Chí Minh",
            "Tp Hcm": "Hồ Chí Minh",
            "Bình Dương": "Hồ Chí Minh",
            "Binh Duong": "Hồ Chí Minh",
            "Bà Rịa Vũng Tàu": "Hồ Chí Minh",
            "Ba Ria Vung Tau": "Hồ Chí Minh",
            "Vũng Tàu": "Hồ Chí Minh",
            "Vung Tau": "Hồ Chí Minh",
            
            # === HÀ NỘI (không sáp nhập) ===
            "Ha Noi": "Hà Nội",
            "Hanoi": "Hà Nội",
            
            # === HUẾ (không sáp nhập) ===
            "Hue": "Huế",
            "Thừa Thiên Huế": "Huế",
            "Thua Thien Hue": "Huế",
            
            # === LÀO CAI (sáp nhập Yên Bái) ===
            "Lao Cai": "Lào Cai",
            "Yên Bái": "Lào Cai",
            "Yen Bai": "Lào Cai",
            "Sapa": "Lào Cai",
            "Sa Pa": "Lào Cai",
            
            # === THÁI NGUYÊN (sáp nhập Bắc Kạn) ===
            "Thai Nguyen": "Thái Nguyên",
            "Bắc Kạn": "Thái Nguyên",
            "Bac Can": "Thái Nguyên",
            
            # === PHÚ THỌ (sáp nhập Vĩnh Phúc, Hòa Bình) ===
            "Phu Tho": "Phú Thọ",
            "Vĩnh Phúc": "Phú Thọ",
            "Vinh Phuc": "Phú Thọ",
            "Hòa Bình": "Phú Thọ",
            "Hoa Binh": "Phú Thọ",
            "Tam Đảo": "Phú Thọ",
            "Tam Dao": "Phú Thọ",
            
            # === BẮC NINH (sáp nhập Bắc Giang) ===
            "Bac Ninh": "Bắc Ninh",
            "Bắc Giang": "Bắc Ninh",
            "Bac Giang": "Bắc Ninh",
            
            # === HƯNG YÊN (sáp nhập Thái Bình) ===
            "Hung Yen": "Hưng Yên",
            "Thái Bình": "Hưng Yên",
            "Thai Binh": "Hưng Yên",
            
            # === HẢI PHÒNG (sáp nhập Hải Dương) ===
            "Hai Phong": "Hải Phòng",
            "Hải Dương": "Hải Phòng",
            "Hai Duong": "Hải Phòng",
            
            # === NINH BÌNH (sáp nhập Hà Nam, Nam Định) ===
            "Ninh Binh": "Ninh Bình",
            "Hà Nam": "Ninh Bình",
            "Ha Nam": "Ninh Bình",
            "Nam Định": "Ninh Bình",
            "Nam Dinh": "Ninh Bình",
            
            # === QUẢNG TRỊ (sáp nhập Quảng Bình) ===
            "Quang Tri": "Quảng Trị",
            "Quảng Bình": "Quảng Trị",
            "Quang Binh": "Quảng Trị",
            
            # === ĐÀ NẴNG (sáp nhập Quảng Nam) ===
            "Da Nang": "Đà Nẵng",
            "Danang": "Đà Nẵng",
            "Quảng Nam": "Đà Nẵng",
            "Quang Nam": "Đà Nẵng",
            "Hội An": "Đà Nẵng",
            "Hoi An": "Đà Nẵng",
            
            # === QUẢNG NGÃI (sáp nhập Kon Tum) ===
            "Quang Ngai": "Quảng Ngãi",
            "Kon Tum": "Quảng Ngãi",
            
            # === GIA LAI (sáp nhập Bình Định) ===
            "Bình Định": "Gia Lai",
            "Binh Dinh": "Gia Lai",
            "Quy Nhơn": "Gia Lai",
            "Quy Nhon": "Gia Lai",
            
            # === KHÁNH HÒA (sáp nhập Ninh Thuận) ===
            "Khanh Hoa": "Khánh Hòa",
            "Nha Trang": "Khánh Hòa",
            "Ninh Thuận": "Khánh Hòa",
            "Ninh Thuan": "Khánh Hòa",
            
            # === LÂM ĐỒNG (sáp nhập Đắk Nông, Bình Thuận) ===
            "Lam Dong": "Lâm Đồng",
            "Đà Lạt": "Lâm Đồng",
            "Da Lat": "Lâm Đồng",
            "Dalat": "Lâm Đồng",
            "Đắk Nông": "Lâm Đồng",
            "Dak Nong": "Lâm Đồng",
            "Bình Thuận": "Lâm Đồng",
            "Binh Thuan": "Lâm Đồng",
            "Phan Thiết": "Lâm Đồng",
            "Phan Thiet": "Lâm Đồng",
            
            # === ĐẮK LẮK (sáp nhập Phú Yên) ===
            "Dak Lak": "Đắk Lắk",
            "Daklak": "Đắk Lắk",
            "Phú Yên": "Đắk Lắk",
            "Phu Yen": "Đắk Lắk",
            
            # === ĐỒNG NAI (sáp nhập Bình Phước) ===
            "Dong Nai": "Đồng Nai",
            "Bình Phước": "Đồng Nai",
            "Binh Phuoc": "Đồng Nai",
            
            # === TÂY NINH (sáp nhập Long An) ===
            "Tay Ninh": "Tây Ninh",
            "Long An": "Tây Ninh",
            
            # === CẦN THƠ (sáp nhập Sóc Trăng, Hậu Giang) ===
            "Can Tho": "Cần Thơ",
            "Cantho": "Cần Thơ",
            "Sóc Trăng": "Cần Thơ",
            "Soc Trang": "Cần Thơ",
            "Hậu Giang": "Cần Thơ",
            "Hau Giang": "Cần Thơ",
            
            # === VĨNH LONG (sáp nhập Bến Tre, Trà Vinh) ===
            "Vinh Long": "Vĩnh Long",
            "Bến Tre": "Vĩnh Long",
            "Ben Tre": "Vĩnh Long",
            "Trà Vinh": "Vĩnh Long",
            "Tra Vinh": "Vĩnh Long",
            
            # === ĐỒNG THÁP (sáp nhập Tiền Giang) ===
            "Dong Thap": "Đồng Tháp",
            "Tiền Giang": "Đồng Tháp",
            "Tien Giang": "Đồng Tháp",
            
            # === CÀ MAU (sáp nhập Bạc Liêu) ===
            "Ca Mau": "Cà Mau",
            "Bạc Liêu": "Cà Mau",
            "Bac Lieu": "Cà Mau",
            
            # === AN GIANG (sáp nhập Kiên Giang) ===
            "Kiên Giang": "An Giang",
            "Kien Giang": "An Giang",
            "Phú Quốc": "An Giang",
            "Phu Quoc": "An Giang",
            "Rạch Giá": "An Giang",
            "Rach Gia": "An Giang",
            
            # === 11 TỈNH KHÔNG SÁP NHẬP ===
            "Cao Bang": "Cao Bằng",
            "Dien Bien": "Điện Biên",
            "Ha Tinh": "Hà Tĩnh",
            "Lai Chau": "Lai Châu",
            "Lang Son": "Lạng Sơn",
            "Nghe An": "Nghệ An",
            "Quang Ninh": "Quảng Ninh",
            "Ha Long": "Quảng Ninh",
            "Halong": "Quảng Ninh",
            "Thanh Hoa": "Thanh Hóa",
            "Son La": "Sơn La",
            "Tuyen Quang": "Tuyên Quang"
        }
        
        return location_map.get(location, location)
    
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