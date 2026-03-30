import socket
import threading
from concurrent.futures import ThreadPoolExecutor

IP_PORT = ("127.0.0.1", 9999)
DEFAULT_WORKERS = 10


def handle_packet(sock, data, addr):
    try:
        msg = data.decode()
        print(f"[{addr}] {msg}")
        reply = f"UDP服务器已收到: {msg}"
        sock.sendto(reply.encode(), addr)
    except ConnectionError:
        print(f"[-] 数据处理异常: {addr}")


def choose_server_mode():
    print("请选择并发模式:")
    print("1) 多线程模式（每个数据包一个线程）")
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


def recv_loop_thread(sock):
    while True:
        data, addr = sock.recvfrom(1024)
        t = threading.Thread(target=handle_packet, args=(sock, data, addr), daemon=True)
        t.start()


def recv_loop_pool(sock, workers):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        while True:
            data, addr = sock.recvfrom(1024)
            executor.submit(handle_packet, sock, data, addr)


def main():
    mode, workers = choose_server_mode()
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(IP_PORT)
    print(
        f"UDP 服务端启动: {IP_PORT[0]}:{IP_PORT[1]} | "
        f"并发模式: {mode}"
        + (f" | 线程池大小: {workers}" if mode == "pool" else "")
    )

    try:
        if mode == "pool":
            recv_loop_pool(server, workers)
        else:
            recv_loop_thread(server)
    except KeyboardInterrupt:
        print("\n收到中断信号，服务端正在关闭...")
    finally:
        server.close()


if __name__ == "__main__":
    main()
