import socket
import threading
import tkinter as tk
from tkinter import messagebox

# 服务器配置
SERVER_HOST = '192.168.0.100'
SERVER_PORT = 8101
# 假设这里有一个合法的十六进制字符串
# hex_string = "48656c6c6f"  # 对应 "Hello" 的十六进制表示
bytes_string0 = bytes.fromhex('01 06 04 0E 00 03 A9 38')  # 打开声音和灯光
bytes_string1 = bytes.fromhex('01 06 04 0E 00 00 E9 39')  # 关闭声光
bytes_string2 = bytes.fromhex('01 06 04 0F 00 01 79 39')  # 音量调为1级

# 存储字节串的字典
byte_strings = {
    '0': bytes_string0,
    '1': bytes_string1,
    '2': bytes_string2
}

# 当前选择的字节串
selected_bytes_string = None

def handle_client(conn, addr):
    global selected_bytes_string
    print(f"新的客户端连接: {addr}")
    try:
        if selected_bytes_string is not None:
            # 发送数据到客户端
            conn.send(selected_bytes_string)
            print(f"已向 {addr} 发送数据")
        else:
            print("未选择要发送的数据，请先点击按钮选择。")
    except ValueError as e:
        print(f"十六进制字符串转换错误: {e}")
    except socket.error as e:
        print(f"Socket 错误: {e}")
    finally:
        # 关闭客户端连接
        conn.close()

def start_server():
    # 创建 TCP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 设置套接字选项，允许地址重用
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 绑定 IP 地址和端口
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    # 开始监听，允许的最大连接数为 5
    server_socket.listen(5)
    print(f"服务器正在监听 {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            # 接受客户端连接
            conn, addr = server_socket.accept()
            # 为每个客户端创建一个新的线程来处理
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
    except KeyboardInterrupt:
        print("服务器关闭")
    finally:
        # 关闭服务器套接字
        server_socket.close()

def select_bytes_string(choice):
    global selected_bytes_string
    selected_bytes_string = byte_strings[choice]
    messagebox.showinfo("选择成功", f"已选择操作: {choice}")

# 创建主窗口
root = tk.Tk()
root.title("服务器控制")

# 创建按钮
button0 = tk.Button(root, text="打开声音和灯光", command=lambda: select_bytes_string('0'))
button0.pack(pady=20)

button1 = tk.Button(root, text="关闭声光", command=lambda: select_bytes_string('1'))
button1.pack(pady=20)

button2 = tk.Button(root, text="音量调为1级", command=lambda: select_bytes_string('2'))
button2.pack(pady=20)

# 启动服务器线程
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

if __name__ == "__main__":
    # 运行主循环
    root.mainloop()