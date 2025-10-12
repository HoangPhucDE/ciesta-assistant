import requests
import json

class APIClient:
    def __init__(self, server_url='http://localhost:5005'):
        self.server_url = server_url.rstrip('/')
        self.session = requests.Session()

    def send_message(self, message, sender_id='user') -> str:
        """Gửi tin nhắn tới Rasa REST API và nhận phản hồi"""
        try:
            payload = {'sender': sender_id, 'message': message}
            url = f"{self.server_url}/webhooks/rest/webhook"
            response = self.session.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )

            # ✅ Xử lý phản hồi
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Ưu tiên text, nếu không có thì in ra toàn bộ nội dung
                    msg = data[0].get("text") or json.dumps(data[0], ensure_ascii=False)
                    return msg
                else:
                    return "⚠️ Không nhận được phản hồi từ bot."
            else:
                return f"❌ Lỗi server: {response.status_code}"

        except requests.ConnectionError:
            return "⚠️ Không kết nối được đến server. Kiểm tra Rasa có đang chạy không?"
        except requests.Timeout:
            return "⏳ Server phản hồi quá lâu. Thử lại sau."
        except Exception as e:
            return f"❌ Lỗi không xác định: {e}"

    def update_server_url(self, new_url):
        """Cập nhật URL server"""
        self.server_url = new_url.rstrip('/')
