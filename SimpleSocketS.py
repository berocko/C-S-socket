#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import threading
from concurrent.futures import ThreadPoolExecutor

IP_PORT = ("127.0.0.1", 9999)
DEFAULT_WORKERS = 10


def handle_client(conn, addr):
    print(f"[+] 客户端已连接: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode()
            print(f"[{addr}] {msg}")
            reply = f"服务器已收到: {msg}"
            conn.sendall(reply.encode())
    except ConnectionError:
        print(f"[-] 连接异常断开: {addr}")
    finally:
        conn.close()
        print(f"[-] 客户端已断开: {addr}")


def choose_server_mode():
    print("请选择并发模式:")
    print("1) 多线程模式（每个连接一个线程）")
    print("2) 线程池模式")
    while True:
        choice = input("输入 1 或 2（默认 1）: ").strip()
        if choice in ("", "1"):
            return "thread", DEFAULT_WORKERS
        if choice == "2":
            workers_text = input(f"请输入线程池大小（默认 {DEFAULT_WORKERS}）: ").strip()
            if workers_text == "":
                return "pool", DEFAULT_WORKERS
            try:
                workers = int(workers_text)
                if workers > 0:
                    return "pool", workers
            except ValueError:
                pass
            print("线程池大小无效，使用默认值。")
            return "pool", DEFAULT_WORKERS
        print("输入无效，请重新输入。")


def serve_with_threads(server):
    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()


def serve_with_thread_pool(server, workers):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        while True:
            conn, addr = server.accept()
            executor.submit(handle_client, conn, addr)


def main():
    ip_port = IP_PORT
    mode, workers = choose_server_mode()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(ip_port)
    server.listen(5)
    print(
        f"TCP 服务端启动: {ip_port[0]}:{ip_port[1]} | "
        f"并发模式: {mode}"
        + (f" | 线程池大小: {workers}" if mode == "pool" else "")
    )

    try:
        if mode == "pool":
            serve_with_thread_pool(server, workers)
        else:
            serve_with_threads(server)
    except KeyboardInterrupt:
        print("\n收到中断信号，服务端正在关闭...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
