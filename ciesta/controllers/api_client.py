import requests
import json
import re

class APIClient:
    def __init__(self, server_url='http://localhost:5005'):
        self.server_url = self._normalize_url(server_url)
        self.session = requests.Session()
        # Thêm headers cho ngrok (tránh warning page)
        self.session.headers.update({
            'ngrok-skip-browser-warning': 'true'
        })

    def _normalize_url(self, url: str) -> str:
        """Chuẩn hóa URL: thêm http:// nếu thiếu, loại bỏ trailing slash"""
        url = url.strip().rstrip('/')
        if not url:
            return 'http://localhost:5005'
        
        # Nếu không có protocol, thêm http://
        if not re.match(r'^https?://', url, re.IGNORECASE):
            # Nếu có ngrok trong URL, dùng https, ngược lại dùng http
            if 'ngrok' in url.lower():
                url = f'https://{url}'
            else:
                url = f'http://{url}'
        
        return url

    def health_check(self, timeout: int = 5) -> bool:
        """Kiểm tra server có đang hoạt động không"""
        try:
            # Thử kết nối đến endpoint status hoặc webhook
            response = self.session.get(
                f"{self.server_url}/status",
                timeout=timeout
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            # Nếu /status không có, thử gửi message test
            try:
                response = self.session.post(
                    f"{self.server_url}/webhooks/rest/webhook",
                    json={'sender': 'health_check', 'message': 'ping'},
                    timeout=timeout
                )
                return response.status_code == 200
            except requests.exceptions.RequestException:
                return False

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
            elif response.status_code == 404:
                return "⚠️ Endpoint không tìm thấy. Kiểm tra URL server có đúng không?"
            else:
                return f"❌ Lỗi server: {response.status_code}"

        except requests.ConnectionError:
            if 'ngrok' in self.server_url.lower():
                return "⚠️ Không kết nối được đến ngrok. Kiểm tra:\n• Ngrok có đang chạy?\n• URL có đúng không?\n• Internet có ổn định?"
            elif 'localhost' in self.server_url or '127.0.0.1' in self.server_url:
                return "⚠️ Không kết nối được đến server local. Kiểm tra Rasa có đang chạy không?"
            else:
                return f"⚠️ Không kết nối được đến server ({self.server_url}).\nKiểm tra:\n• Server có đang chạy?\n• IP/URL có đúng không?\n• Firewall có chặn không?"
        except requests.Timeout:
            return "⏳ Server phản hồi quá lâu. Có thể:\n• Mạng chậm\n• Server quá tải\n• Ngrok tunnel bị gián đoạn"
        except requests.exceptions.SSLError:
            return "⚠️ Lỗi SSL. Kiểm tra URL có đúng protocol (http/https) không?"
        except Exception as e:
            return f"❌ Lỗi không xác định: {str(e)[:100]}"

    def update_server_url(self, new_url):
        """Cập nhật URL server"""
        self.server_url = self._normalize_url(new_url)
        # Reset session để áp dụng URL mới
        self.session = requests.Session()
        self.session.headers.update({
            'ngrok-skip-browser-warning': 'true'
        })

    def get_connection_info(self) -> dict:
        """Lấy thông tin về kết nối hiện tại"""
        url = self.server_url
        info = {
            'url': url,
            'type': 'Unknown'
        }
        
        if 'ngrok' in url.lower():
            info['type'] = 'Ngrok'
        elif 'localhost' in url or '127.0.0.1' in url:
            info['type'] = 'Local'
        else:
            info['type'] = 'LAN'
        
        return info

    @staticmethod
    def get_ngrok_url(ngrok_api_url: str = 'http://localhost:4040', timeout: int = 3):
        """
        Lấy ngrok public URL từ ngrok local API
        
        Args:
            ngrok_api_url: URL của ngrok API (mặc định localhost:4040)
            timeout: Timeout cho request
            
        Returns:
            Tuple (public_url, error_message)
            - public_url: URL công khai từ ngrok (None nếu lỗi)
            - error_message: Thông báo lỗi (empty nếu thành công)
        """
        try:
            # Gọi ngrok API để lấy thông tin tunnels
            response = requests.get(
                f"{ngrok_api_url}/api/tunnels",
                timeout=timeout
            )
            
            if response.status_code != 200:
                return None, f"Ngrok API trả về status {response.status_code}"
            
            data = response.json()
            
            # Tìm tunnel có protocol https (ưu tiên) hoặc http
            tunnels = data.get('tunnels', [])
            if not tunnels:
                return None, "Không tìm thấy tunnel nào. Kiểm tra ngrok có đang chạy không?"
            
            # Ưu tiên https tunnel
            https_tunnel = None
            http_tunnel = None
            
            for tunnel in tunnels:
                public_url = tunnel.get('public_url', '')
                if public_url.startswith('https://'):
                    https_tunnel = public_url
                elif public_url.startswith('http://') and not http_tunnel:
                    http_tunnel = public_url
            
            # Trả về https nếu có, nếu không thì http
            if https_tunnel:
                return https_tunnel, ""
            elif http_tunnel:
                return http_tunnel, ""
            else:
                return None, "Không tìm thấy tunnel hợp lệ"
                
        except requests.exceptions.ConnectionError:
            return None, "Không kết nối được đến ngrok API. Kiểm tra:\n• Ngrok có đang chạy?\n• Ngrok API có ở localhost:4040?"
        except requests.exceptions.Timeout:
            return None, "Ngrok API phản hồi quá lâu"
        except json.JSONDecodeError:
            return None, "Ngrok API trả về dữ liệu không hợp lệ"
        except Exception as e:
            return None, f"Lỗi: {str(e)[:100]}"
