#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
视频帧提取工具

该脚本用于将MP4视频分解为单独的帧，并按照时间戳命名保存到指定目录。
用法：python video2frames.py [视频文件路径]
"""

import cv2
import os
import sys
import time
import argparse
from datetime import datetime
from tqdm import tqdm


def ensure_dir(directory):
    """
    确保目录存在，如果不存在则创建
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")


def resize_image(image, target_width=480):
    """
    调整图片尺寸，保持宽高比
    """
    height, width = image.shape[:2]
    # 计算缩放比例
    scale = target_width / width
    # 计算新的高度
    target_height = int(height * scale)
    # 调整图片尺寸
    return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)


def extract_frames(video_path, output_dir):
    """
    从视频中提取帧并按时间戳命名保存
    """
    # 确保输出目录存在
    ensure_dir(output_dir)
    
    # 打开视频文件
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        print(f"错误: 无法打开视频文件 {video_path}")
        return False
    
    # 获取视频信息
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps > 0 else 0
    
    print(f"视频信息:")
    print(f"  - 帧率: {fps} fps")
    print(f"  - 总帧数: {frame_count}")
    print(f"  - 时长: {duration:.2f} 秒")
    
    # 获取当前时间作为基准时间（纳秒）
    current_time_ns = int(time.time() * 1_000_000_000)
    print(f"  - 基准时间: {datetime.fromtimestamp(current_time_ns / 1_000_000_000).strftime('%Y-%m-%d %H:%M:%S.%f')}")
    
    # 提取帧
    frame_index = 0
    success = True
    
    # 创建增强的进度条
    pbar = tqdm(
        total=frame_count,
        desc="提取帧",
        unit="帧",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
        postfix={"已完成": "0%", "当前帧": 0, "视频时间": "0.00秒"},
        dynamic_ncols=True
    )
    
    start_time = time.time()
    
    while success:
        # 读取下一帧
        success, frame = video.read()
        
        if success:
            # 调整图片尺寸
            frame = resize_image(frame)
            
            # 计算当前帧的时间戳（纳秒）：当前时间 + 帧偏移时间
            frame_time_ns = int((frame_index / fps) * 1_000_000_000)
            timestamp_ns = current_time_ns + frame_time_ns
            
            # 保存帧为PNG文件，使用时间戳作为文件名
            output_path = os.path.join(output_dir, f"{timestamp_ns}.png")
            cv2.imwrite(output_path, frame)
            
            # 更新进度条和附加信息
            frame_index += 1
            current_video_time = frame_index / fps if fps > 0 else 0
            completion_percentage = f"{(frame_index / frame_count * 100):.1f}%" if frame_count > 0 else "未知"
            
            pbar.set_postfix({
                "已完成": completion_percentage,
                "当前帧": frame_index,
                "视频时间": f"{current_video_time:.2f}秒"
            })
            pbar.update(1)
    
    # 关闭进度条
    pbar.close()
    
    video.release()
    
    # 计算总处理时间
    total_time = time.time() - start_time
    processing_rate = frame_index / total_time if total_time > 0 else 0
    
    print(f"\n完成! 共提取 {frame_index} 帧到 {output_dir}")
    print(f"处理用时: {total_time:.2f}秒, 平均速度: {processing_rate:.2f}帧/秒")
    return True


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="从视频中提取帧并按时间戳命名")
    parser.add_argument("video_path",default="test.mp4" ,help="输入视频文件的路径")
    parser.add_argument("--output-dir", "-o", default="main_folder/mav0/cam0/data",
                        help="输出目录路径 (默认: main_folder/mav0/cam0/data)")
    args = parser.parse_args()
    
    # 获取视频文件的绝对路径
    video_path = os.path.abspath(args.video_path)
    if not os.path.isfile(video_path):
        print(f"错误: 视频文件不存在 {video_path}")
        return 1
    
    # 获取输出目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    output_dir = os.path.join(project_root, args.output_dir)
    
    print(f"视频文件: {video_path}")
    print(f"输出目录: {output_dir}")
    
    # 提取帧
    success = extract_frames(video_path, output_dir)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())