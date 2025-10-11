import requests
import json

class APIClient:
    def __init__(self, server_url='http://localhost:5005'):
        self.server_url = server_url
        self.session = requests.Session()

    def send_message(self, message, sender_id='user') -> str:
        try:
            payload = {'sender': sender_id, 'message': message}
            response = self.session.post(
                f"{self.server_url}/webhooks/rest/webhook",
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                data = response.json()
                if data:
                    return data[0]['text']
            return "Xin lỗi, không hiểu. Hãy thử lại!"
        except requests.RequestException:
            return "Lỗi server. Kiểm tra Rasa chạy chưa?"

    def update_server_url(self, new_url):
        self.server_url = new_url