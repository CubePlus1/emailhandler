"""
邮件认证工具 - CLI 应用
功能：等待邮件、自动处理验证链接
"""

from emailhandler import EmailMonitor


def main():
    """主函数"""
    
    print("\n" + "="*60)
    print("  邮件认证工具 v2.0")
    print("="*60)
    print("\n📋 说明：")
    print("  1. 确保 email_receiver.py 已启动")
    print("  2. 此程序将等待邮件验证链接")
    print("  3. 收到邮件后自动处理验证")
    print("\n" + "="*60 + "\n")
    
    # 配置
    api_url = 'http://localhost:5000'
    max_wait = 300  # 最多等待 5 分钟
    
    print(f"⚙️ 配置:")
    print(f"  → 邮件服务: {api_url}")
    print(f"  → 超时时间: {max_wait} 秒\n")
    
    # 创建邮件监控
    monitor = EmailMonitor(api_url=api_url)
    
    print("🔔 开始监听邮件...\n")
    
    try:
        # 等待邮件并处理验证链接
        result = monitor.wait_and_handle_verification_link(max_wait=max_wait)
        
        print("\n" + "="*60)
        
        if result.get('success'):
            print("✅ 操作成功！")
            print("="*60)
            print(f"\n✓ 验证链接已处理")
            print(f"🔑 验证 ID: {result.get('verification_id', 'N/A')}")
            print(f"💬 {result.get('message', '验证完成')}\n")
        else:
            print("❌ 操作失败")
            print("="*60)
            print(f"\n⚠️ {result.get('message', '未知错误')}\n")
            
            print("🔍 故障排除：")
            print("  1. 检查 email_receiver.py 是否运行")
            print("  2. 检查邮件是否已发送到配置的地址")
            print("  3. 检查验证链接是否有效")
            print("  4. 检查网络连接\n")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 用户中断操作\n")
    except Exception as e:
        print(f"\n\n❌ 异常错误: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
