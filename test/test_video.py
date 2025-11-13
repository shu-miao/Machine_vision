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
                                                    ship_mmsi = ais_track_dict[int(box.id)][3],
                                                    distance = ais_track_dict[int(box.id)][4]
                                            )
                                        # logging.info(f"准备广播数据: detection_result{detection_result}")
                                        # 使用线程池执行异步任务
                                            # self.executor_callback.submit(self._run_async_callback, detection_result_callback, detection_result_ais)
                                        # logging.info(f"发布广播任务: detection_result{detection_result}")

                                        # 使用专用线程池异步推到redis，避免阻塞检测
                                        # self.executor_redis.submit(self._async_push_to_redis, camera_id, detection_result.to_dict())
                                            # detection_result_dict[str(int(box.id))] = detection_result_ais.to_dict()
                                            detection_result_list.append(detection_result_ais.to_dict())

                                        elif ais_hit >= 60:
                                            detection_result = DetectionResult(
                                                    task_id=task_id,
                                                    camera_id=camera_id,
                                                    device_id=device_id,
                                                    target_class=class_str, # 类别
                                                    confidence=box.conf.item(), # 置信度
                                                    track_id=int(box.id),
                                                    marker_x=(x1 + x2) * 0.5 / width, # 中心x坐标
                                                    marker_y=(y1 + y2) * 0.5 / height, #中心y坐标
                                                    alarm_id=alarm_id,
                                                    # frame_data=frame_data,
                                                    camera_high=self.camera_high, # 高度
                                                    camera_fangwei=self.camera_fangwei, # 方位
                                                    camera_fu=self.camera_fu, # 俯角
                                                    box_lable = box_lable # 检测框
                                                )                                            
                                            ais_data = self._notify_callbacks(detection_result)
                                            ais_track_dict[int(box.id)] = ais_data
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
                                                    ship_mmsi = ais_track_dict[int(box.id)][3],
                                                    distance = ais_track_dict[int(box.id)][4]
                                            )
                                            # ais_hit = 0
                                            # 使用线程池执行异步任务
                                            # logging.info(f"准备广播数据detection_result_ais: {detection_result_ais}")
                                            # self.executor_callback.submit(self._run_async_callback, detection_result_callback, detection_result_ais)
                                            # logging.info(f"发布广播任务detection_result_ais: {detection_result_ais}")

                                            # 使用专用线程池异步推到redis，避免阻塞检测
                                            # self.executor_redis.submit(self._async_push_to_redis, camera_id, detection_result_ais.to_dict())
                                            # detection_result_dict[str(int(box.id))] = detection_result_ais.to_dict()
                                            detection_result_list.append(detection_result_ais.to_dict())
                                            detection_result_ws_dict['data'] = detection_result_list

                                            # 图片保存逻辑，只有在第一次发现并尝试定位目标时才保存
                                            # if str(int(box.id)) not in boxid_set:
                                            #     boxid_set.add(str(int(box.id)))
                                            #     # 保存图片到本地
                                            #     img_with_boxes = results[0].plot()
                                            #     img_path = f'/home/warning_py/pic/ship_detection/{camera_id}_{time.strftime("%Y%m%d_%H%M%S", time.localtime())}.jpg'
                                            #     cv2.imwrite(img_path, img_with_boxes)
                                            #     logging.info(f"保存图片到本地: {img_path}")

                                        else:
                                            detection_result = DetectionResult(
                                                    task_id=task_id,
                                                    camera_id=camera_id,
                                                    device_id=device_id,
                                                    target_class=class_str, # 类别
                                                    confidence=box.conf.item(), # 置信度
                                                    track_id=int(box.id),
                                                    marker_x=(x1 + x2) * 0.5 / width, # 中心x坐标
                                                    marker_y=(y1 + y2) * 0.5 / height, #中心y坐标
                                                    alarm_id=alarm_id,
                                                    # frame_data=frame_data,
                                                    camera_high=self.camera_high, # 高度
                                                    camera_fangwei=self.camera_fangwei, # 方位
                                                    camera_fu=self.camera_fu, # 俯角
                                                    box_lable = box_lable # 检测框
                                                )
                                            # self.executor_callback.submit(self._run_async_callback, detection_result_callback, detection_result_ais)
                                            # detection_result_dict[str(int(box.id))] = detection_result.to_dict()
                                            detection_result_list.append(detection_result.to_dict())
                                
                                self.executor_callback.submit(self._run_async_callback, detection_result_callback, detection_result_ws_dict)
                                
                                # self.executor_redis.submit(self._async_push_to_redis, camera_id, detection_result_dict)

                    if ais_hit >= 60:
                        ais_hit = 0

                    if detected:
                        consecutive_detections += 1
                    else:
                        consecutive_detections = 0

                except Exception as e:
                    logging.error(f"处理帧时出错: {e}")
                    time.sleep(0.1)  # 出错时短暂休眠
                    continue

            video_stream.stop()  # 停止取流
            boxid_set.clear()  # 当任务结束时，清空目标id集合
            ais_track_dict.clear()
            logging.info(f"{camera_id}的检测任务已终止，停止视频流处理。")

        except Exception as e:
            logging.error(f"检测任务初始化失败: {e}")
