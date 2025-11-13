'''测试视频检测'''


def _detection_worker(self, task_id: str, video_url: str, camera_id: str, device_id: str):
        """检测工作线程"""
        try:
            video_stream = VideoStream(video_url)
            consecutive_detections = 0  # 连续检测计数器
            detection_threshold = config_data['detection_threshold']  # 连续检测的阈值
            boxid_set = set()
            ais_dict = {}

            ais_hit = 60 # 查库的间隔，以帧为单位
            
            detection_result_ws_dict = {} # ws用
            detection_result_ws_dict['task_id'] = task_id
            detection_result_ws_dict['camera_id'] = camera_id

            # 获取视频的帧率和尺寸
            # fps = int(video_stream.stream.get(cv2.CAP_PROP_FPS))
            # width = int(video_stream.stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            # height = int(video_stream.stream.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # # 创建视频写入对象
            # fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            # output_video = cv2.VideoWriter('../file/detection_output.mp4', fourcc, fps,
            #                                (width, height))
            ais_data = None
            ais_track_dict = {}
            while task_id in self.active_tasks and self.active_tasks[task_id]['running']:
                try:
                    frame = video_stream.read()
                    if frame is None:
                        time.sleep(0.01)  # 短暂休眠
                        continue

                    # 更新帧计数
                    self.active_tasks[task_id]['frame_count'] += 1

                    height, width, _ = frame.shape
                    results = self.model.track(
                                               frame,
                                               verbose=False,
                                               persist=True,
                                               conf=0.6,
                                               iou=0.4,
                                               )
                    ais_hit += 1
                    detected = False  # 当前帧是否检测到目标

                    # detection_result_dict = {} # reids用
                    detection_result_list = []
                    

                    for result in results:
                        boxes = result.boxes
                        if boxes:
                            detected = True
                            if consecutive_detections >= detection_threshold:
                                for box in boxes:
                                    if box.conf.item() > config_data['conf_threshold'] and box.id is not None:
                                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                                        box_lable = {'x1':x1, 'y1':y1, 'x2':x2, 'y2':y2}
                                        # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                        class_str = config_data['class_dict'][str(box.cls.item())]
                                        alarm_id = str(uuid.uuid4())
                                        # cv2.putText(frame, f'{class_str} {box.conf[0]:.3f}', (x1, y1 - 10),
                                        #             cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
                                        
                                        

                                        if int(box.id) in ais_track_dict and ais_track_dict[int(box.id)] is not None:
                                            
                                            detection_result_ais = DetectionResult_AIS(
                                                    task_id=task_id,
                                                    camera_id=camera_id,
                                                    device_id=device_id,
                                                    target_class=class_str,
                                                    confidence=box.conf.item(),
                                                    track_id=int(box.id),
                                                    marker_x=(x1 + x2) * 0.5 / width,
                                                    marker_y=(y1 + y2) * 0.5 / height,
                                                    alarm_id=alarm_id,
                                                    # frame_data=frame_data,
                                                    camera_high=self.camera_high, # 高度
                                                    camera_fangwei=self.camera_fangwei, # 方位
                                                    camera_fu=self.camera_fu, # 俯角
                                                    box_lable = box_lable, # 检测框
                                                    new_lon=ais_track_dict[int(box.id)][0],
                                                    new_lat=ais_track_dict[int(box.id)][1],
                                                    ship_name = ais_track_dict[int(box.id)][2],
                                                    ship_mmsi = ais_track_d