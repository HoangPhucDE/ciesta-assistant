"""Simple parse test script to call local Rasa /model/parse endpoint.

Usage: python utils/parse_test.py

This script sends a small set of test messages to the local Rasa server (http://localhost:5005/model/parse)
and prints the parse output (intent + entities). It's helpful to validate whether RegexEntityExtractor
+ lookup table are picked up before DIET.
"""
import requests
import json

TEST_MESSAGES = [
    "Giới thiệu về Sài Gòn",
    "Ẩm thực Đà Nẵng",
    "Hãy kể một câu chuyện",
    "Giới thiệu về HCM",
    "Địa điểm du lịch Đà Lạt",
    "Xin chào",
]

URL = "http://localhost:5005/model/parse"


def parse(msg):
    try:
        resp = requests.post(URL, json={"text": msg}, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    for m in TEST_MESSAGES:
        print("---")
        print("Message:", m)
        out = parse(m)
        print(json.dumps(out, ensure_ascii=False, indent=2))
