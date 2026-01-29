import requests

url = 'http://127.0.0.1:5000/webhook/email'
payload = {
    'from': 'tester@example.com',
    'to': '5000@example.com',
    'subject': '测试邮件',
    'html': '<a href="https://example.com/verify/abc123def456ab123def456">点击验证</a>',
    'text': '验证链接 https://example.com/verify/abc123def456ab123def456'
}

r = requests.post(url, json=payload)
print(r.status_code)
print(r.text)
