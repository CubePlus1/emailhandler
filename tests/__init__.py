"""
测试示例 - EmailHandler 使用演示
"""

from emailhandler import EmailMonitor, VerificationLinkHandler, click_verification_link


def test_link_extraction():
    """测试链接提取"""
    print("\n=== 测试 1: 链接提取 ===\n")
    
    handler = VerificationLinkHandler()
    
    # 测试各种格式的链接
    test_urls = [
        "https://verify.example.com?verificationId=abc123def456ab123def456",
        "https://example.com/verify/abc123def456ab123def456",
        "https://example.com?id=abc123def456ab123def456",
    ]
    
    for url in test_urls:
        vid = handler.extract_verification_id(url)
        print(f"URL: {url[:60]}...")
        print(f"ID: {vid}\n")


def test_api_polling():
    """测试 API 轮询"""
    print("\n=== 测试 2: API 轮询 ===\n")
    
    monitor = EmailMonitor()
    
    print("尝试获取验证链接 (超时 10 秒)...")
    result = monitor.get_verification_link_from_api(max_wait=10)
    
    if result['success']:
        print(f"✓ 获取成功")
        print(f"链接: {result['link']}")
        print(f"主题: {result['subject']}")
    else:
        print(f"✗ {result.get('message', '未知错误')}")


def test_link_click():
    """测试链接点击"""
    print("\n=== 测试 3: 链接点击 ===\n")
    
    # 这是一个示例链接，实际使用时需要真实链接
    example_url = "https://httpbin.org/get?verificationId=abc123def456ab123def456"
    
    print(f"测试链接: {example_url}\n")
    
    result = click_verification_link(example_url, timeout=10)
    
    print(f"成功: {result['success']}")
    print(f"状态码: {result.get('status_code')}")
    print(f"验证 ID: {result.get('verification_id')}")
    print(f"消息: {result.get('message')}")


def test_complete_flow():
    """测试完整流程"""
    print("\n=== 测试 4: 完整流程 ===\n")
    
    monitor = EmailMonitor()
    
    print("启动完整流程 (超时 30 秒)...\n")
    
    result = monitor.wait_and_handle_verification_link(max_wait=30)
    
    print(f"成功: {result['success']}")
    print(f"验证 ID: {result.get('verification_id')}")
    print(f"消息: {result.get('message')}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  EmailHandler - 测试演示")
    print("="*60)
    
    print("\n说明:")
    print("  测试 1: 链接提取（无需服务）")
    print("  测试 2: API 轮询（需要邮件服务）")
    print("  测试 3: 链接点击（需要真实链接）")
    print("  测试 4: 完整流程（需要邮件和服务）")
    
    # 运行测试 1（总是可用）
    try:
        test_link_extraction()
    except Exception as e:
        print(f"测试 1 失败: {e}")
    
    # 其他测试可选
    print("\n" + "="*60)
    print("✓ 测试演示完成")
    print("="*60 + "\n")
