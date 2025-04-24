import socket
import threading
import logging
from datetime import datetime
from odoo import api, models
from odoo.modules.registry import Registry
_logger = logging.getLogger(__name__)

class RtxDtuDataService(models.AbstractModel):
    _name = 'dtu.data.service'
    _description = 'DTU Data Collection Service'

    def start_data_collection(self):
        try:
            # 创建一个TCP套接字
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            _logger.error(f"Failed to create socket: {e}")
            return

        # 绑定IP地址和端口
        # server_address = ('172.29.215.76', 5000)
        server_address = ('172.20.20.122', 5000)
        try:
            server_socket.bind(server_address)
        except socket.error as e:
            _logger.error(f"Failed to bind socket to address {server_address}: {e}")
            server_socket.close()
            return

        # 开始监听连接
        try:
            server_socket.listen(1)
        except socket.error as e:
            _logger.error(f"Failed to start listening on socket: {e}")
            server_socket.close()
            return

        _logger.info('Waiting for a connection...')

        while True:
            # 接受客户端连接
            connection, client_address = server_socket.accept()
            try:
                # 接收数据
                data = connection.recv(1024)
                if data:
                    # 解码接收到的数据
                    data_str = data.decode('utf-8', errors='ignore')
                    # 清理数据，移除空字符
                    clean_data_str = data_str.replace('\x00', '')
                    # 为当前线程创建独立的环境
                    self._process_data(clean_data_str)
            finally:
                # 关闭连接
                connection.close()

    def _process_data(self, data_str):
        # 获取当前数据库的注册表
        db_registry = Registry(self.env.cr.dbname)
        with db_registry.cursor() as new_cr:
            # 为当前线程创建新的环境
            new_env = api.Environment(new_cr, self.env.uid, self.env.context)
            pv = {
                "name": data_str['name'],
                "imei": data_str['imei'],
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": data_str['model'],
                "version": data_str['version'],
                "running_time": data_str['running_time'],
                "remaining_memory": data_str['remaining_memory'],
                "signal_strength": data_str['signal_strength'],
                "pressure": data_str['pressure'],  # 压力
                "traffic": data_str['traffic'],  # 流量
                "liquid_level": data_str['liquid_level'],  # 液位
                "temperature": data_str['temperature'],  # 温度
                "atmospheric_pressure": data_str['atmospheric_pressure'],  # 气压
                "humidity": data_str['humidity'],  # 湿度
                "gps_longitude": data_str['gps_longitude'],
                "gps_latitude": data_str['gps_latitude'],
                "gsm_longitude": data_str['gsm_longitude'],
                "gsm_latitude": data_str['gsm_latitude'],
            }
            try:
                # 调用Odoo模型保存数据
                new_env['dtu.data'].create(pv)
                _logger.info(f'Received data: {data_str}')
                # 提交事务
                new_cr.commit()
            except Exception as e:
                # 回滚事务
                new_cr.rollback()
                _logger.info(f"Error processing data: {e}")

    def start_service(self):
        # 启动数据采集线程
        thread = threading.Thread(target=self.start_data_collection)
        thread.start()

    def create_data_str(self):
        explain_obj = self.env['dtu.data']
        project_obj = self.env['project.project']
        location_obj = self.env['project.map.location']
        imei_records = [
        ]
        for imeis in imei_records:
            for index, imei in enumerate(imeis):
                traffic = random.randint(200, 300),  # 流量
                if index == 0:
                    # 写入管道第一个数据到泵站
                    location_id = location_obj.search([('imei', '=', f'{imei[1]}')])
                    location_id.write({'real_input_traffic': traffic[0]})
                    # 写入管道第一个数据到项目
                    project_id = project_obj.search([('name', '=', f'{imei[0]}')])
                    project_id.write({'real_input_traffic': traffic[0]})
                if index == len(imeis) - 1:
                    # 写入管道最后一个数据到泵站
                    location_id = location_obj.search([('imei', '=', f'{imei[1]}')])
                    location_id.write({'real_output_traffic': traffic[0]})
                    # 写入管道最后一个数据到项目
                    project_id = project_obj.search([('name', '=', f'{imei[0]}')])
                    project_id.write({'real_output_traffic': traffic[0]})
                pv = {
                    "name": imei[0],
                    "imei": imei[1],
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "model": False,
                    "version": False,
                    "running_time": False,
                    "remaining_memory": False,
                    "signal_strength": False,
                    "pressure": random.randint(90, 105),     # 压力
                    "traffic": traffic[0],     # 流量
                    "liquid_level": random.randint(50, 70),     # 液位
                    "temperature": random.randint(30, 55),     # 温度
                    "atmospheric_pressure": random.randint(10, 25),     # 气压
                    "humidity": random.randint(40, 70),     # 湿度
                    "gps_longitude": False,
                    "gps_latitude": False,
                    "gsm_longitude": imei[2],
                    "gsm_latitude": imei[3],
                }
                _logger.info(f"{pv}")
                try:
                    # 直接使用 pv 字典创建记录
                    record = explain_obj.create(pv)
                    if record:
                        _logger.info("Data created successfully.")
                        # 手动提交事务，确保数据实时写入
                        self.env.cr.commit()
                    else:
                        _logger.error("Failed to create data.")
                except Exception as e:
                    _logger.error(f"Error creating data: {e}")
                    # 回滚事务，防止数据不一致
                    self.env.cr.rollback()
