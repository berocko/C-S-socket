#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import threading

IP_PORT = ("127.0.0.1", 9999)


def recv_loop(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("服务器已关闭连接")
                break
            print("\n[服务器]:", data.decode())
        except ConnectionError:
            print("连接异常，接收线程退出")
            break


def send_loop(sock):
    while True:
        msg = input("输入消息(输入 exit 退出): ").strip()
        if msg.lower() == "exit":
            break
        if not msg:
            continue
        try:
            sock.sendall(msg.encode())
        except ConnectionError:
            print("发送失败，连接已断开")
            break


def main():
    server_addr = IP_PORT

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(server_addr)
    print(f"已连接服务器: {server_addr[0]}:{server_addr[1]}")

    t = threading.Thread(target=recv_loop, args=(client,), daemon=True)
    t.start()

    send_loop(client)
    client.close()


if __name__ == "__main__":
    main()
