import requests
import json

def show_received_emails():
    """显示邮件接收服务接收到的所有邮件"""
    try:
        # 获取所有邮件
        response = requests.get('http://127.0.0.1:5000/emails', timeout=5)
        data = response.json()
        
        print("\n" + "="*60)
        print("  接收到的邮件列表")
        print("="*60)
        
        if data['count'] == 0:
            print("\n  ⚠️  暂无邮件")
        else:
            print(f"\n  📧 共接收 {data['count']} 封邮件\n")
            
            for idx, email in enumerate(data['emails'], 1):
                print(f"--- 邮件 {idx} ---")
                print(f"发送者: {email.get('from', 'N/A')}")
                print(f"收件人: {email.get('to', 'N/A')}")
                print(f"主题: {email.get('subject', 'N/A')}")
                print(f"时间: {email.get('timestamp', 'N/A')}")
                
                if email.get('verification_link'):
                    print(f"验证链接: {email['verification_link']}")
                
                print(f"内容预览:")
                html = email.get('html', '')
                text = email.get('text', '')
                content = html if html else text
                if content:
                    preview = content[:100] + '...' if len(content) > 100 else content
                    print(f"  {preview}")
                else:
                    print("  (无内容)")
                print()
        
        print("="*60 + "\n")
        
        # 也显示最新的验证链接
        try:
            link_resp = requests.get('http://127.0.0.1:5000/verification_link', timeout=5)
            if link_resp.status_code == 200:
                link_data = link_resp.json()
                print("\n✓ 最新验证链接:")
                print(f"  链接: {link_data['link']}")
                print(f"  主题: {link_data['subject']}")
                print(f"  时间: {link_data['timestamp']}\n")
        except:
            pass
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到邮件接收服务 (127.0.0.1:5000)")
        print("   请确保邮件接收服务已启动: python email_receiver.py")
    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    show_received_emails()
