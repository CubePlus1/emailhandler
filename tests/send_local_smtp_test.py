# 本地 SMTP 测试脚本
# 用途：在本地启动一个 SMTP DebuggingServer（监听 5000），
# 然后通过 smtplib 发送一封测试邮件到目标地址（若没有域名，则补全为 @example.com）。

import argparse
import threading
import time
import smtpd
import asyncore
import smtplib
from email.message import EmailMessage


class _DebuggingServer(smtpd.DebuggingServer):
    # 继承以便在需要时扩展
    pass


def start_debug_smtp(port: int = 5000):
    server = _DebuggingServer(("127.0.0.1", port), None)

    thread = threading.Thread(target=asyncore.loop, kwargs={"timeout": 1})
    thread.daemon = True
    thread.start()

    # 给服务器一点时间启动
    time.sleep(0.2)
    return server, thread


def send_test_email(to_addr: str, subject: str = "测试邮件", body: str = "这是一封本地测试邮件。", port: int = 5000, from_addr: str = "tester@example.com"):
    if "@" not in to_addr:
        to_addr = f"{to_addr}@example.com"

    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP("127.0.0.1", port) as s:
        s.send_message(msg)

    return to_addr


def main():
    parser = argparse.ArgumentParser(description="在本地启动 SMTP DebuggingServer 并发送测试邮件")
    parser.add_argument("--to", default="5000", help="接收地址，若无域名将补全为 @example.com（默认: 5000）")
    parser.add_argument("--port", type=int, default=5000, help="本地 SMTP 监听端口（默认: 5000）")
    args = parser.parse_args()

    print(f"启动本地 SMTP DebuggingServer (127.0.0.1:{args.port})...")
    server, thread = start_debug_smtp(port=args.port)

    print(f"发送测试邮件到: {args.to} (通过本地端口 {args.port})")
    to_addr = send_test_email(args.to, port=args.port)

    # 等待短暂时间以便 DebuggingServer 打印收到的邮件
    time.sleep(0.5)

    print("测试邮件已发送。请查看上方 DebuggingServer 输出以确认接收内容。")


if __name__ == "__main__":
    main()
