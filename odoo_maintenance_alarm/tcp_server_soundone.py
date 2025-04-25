import socket

# 定义指令
d11 = bytes.fromhex('01 06 04 0E 00 03 A9 38')  # 打开声音和灯光
d12 = bytes.fromhex('01 06 04 0E 00 00 E9 39')  # 关闭声光
d13 = bytes.fromhex('01 06 04 0F 00 01 79 39')  # 音量调为1级

def connect_to_device(ip, port):
    """
    连接到设备
    :param ip: 设备的 IP 地址
    :param port: 设备的端口号
    :return: 连接对象或 None
    """
    try:
        # 创建 Socket 对象
        socket_server = socket.socket()
        # 绑定 IP 地址和端口
        socket_server.bind((ip, port))
        # 监听端口
        socket_server.listen(1)
        print(f"正在监听 {ip}:{port}...")
        # 等待客户端连接
        conn, address = socket_server.accept()
        print(f"接收到了客户端的连接，客户端的信息是：{address}")
        return conn, socket_server
    except Exception as e:
        print(f"连接设备时发生异常: {e}")
        return None, None

def send_command_to_device(conn, command):
    """
    向设备发送指令
    :param conn: 连接对象
    :param command: 要发送的指令
    """
    try:
        # 发送指令
        conn.send(command)
        print(f"已发送指令: {command.hex()}")
        # 接收设备的响应
        response = conn.recv(1024)
        if response:
            print(f"接收到设备的响应：{response.hex()}")
    except Exception as e:
        print(f"发送指令时发生异常: {e}")

def main():
    # 设备的 IP 地址和端口号
    ip = "192.168.0.100"
    port = 8101

    # 连接到设备
    conn, socket_server = connect_to_device(ip, port)
    if conn and socket_server:
        try:
            # 发送指令
            # send_command_to_device(conn, d11)

            # 可以根据需要发送更多指令
            # send_command_to_device(conn, d12)
            send_command_to_device(conn, d13)

        except KeyboardInterrupt:
            print("用户手动中断程序")
        finally:
            # 关闭连接
            conn.close()
            socket_server.close()
            print("连接已关闭")

if __name__ == "__main__":
    main()