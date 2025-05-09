from onvif import ONVIFCamera
from time import sleep

# 连接到摄像头
camera = ONVIFCamera('192.168.1.228', 80, 'admin', 'htzy@0851')  # 替换为您的摄像头IP和登录信息

# 获取 PTZ 服务
ptz_service = camera.create_ptz_service()

# 获取媒体服务
media_service = camera.create_media_service()

# 获取第一个配置文件
profiles = media_service.GetProfiles()
profile_token = profiles[0].token

# 手动控制云台进行一次简单的平移操作
ptz_service.ContinuousMove({'ProfileToken': profile_token, 'Velocity': {'PanTilt': {'x': 0.1, 'y': 0.0}}})

# 等待几秒钟，云台开始移动
sleep(5)

# 停止云台移动
ptz_service.Stop({'ProfileToken': profile_token})

# 获取 PTZ 状态
status = ptz_service.GetStatus({'ProfileToken': profile_token})

print("PTZ Status:", status)

# 打印 PTZ 状态（水平、垂直和变焦）
if status and status.Position:
    print("Pan: ", status.Position.PanTilt.x)
    print("Tilt: ", status.Position.PanTilt.y)
    print("Zoom: ", status.Position.Zoom.x)
else:
    print("PTZ Position is not available.")
