import requests

# 您的API密钥
api_key = "GJHBZ-5BM6X-YVK4L-ZFHJ4-5XTOF-S3B4L"

# 起点和终点坐标
from_coords = "44.3205344,89.3099585"  # 示例坐标：北京
to_coords = "44.3829802,89.3369684"  # 示例坐标：上海

# 构建请求URL
url = "https://apis.map.qq.com/ws/distance/v1/"
# url = f"https://apis.map.qq.com/ws/distance/v1?from={from_coords}&to={to_coords}&key={api_key}&mode=straight"
# url = f"https://apis.map.qq.com/ws/distance/v1/matrix?from={from_coords}&to={to_coords}&key={api_key}&mode=driving"
params = {
    "key": api_key,
    "mode": "driving",  # 可选值：‘driving’驾车,‘walking’步,默认：'walking’,‘straight’直线
    "from": from_coords,
    "to": to_coords,
}
# 发送GET请求
response = requests.get(url, params=params, timeout=10)
# 解析响应
data = response.json()
print(data)
