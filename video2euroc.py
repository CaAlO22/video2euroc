#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
视频转EuRoC数据集工具

该脚本用于将视频文件转换为EuRoC格式的数据集，按顺序执行以下步骤：
1. 从视频中提取帧并按时间戳命名
2. 生成时间戳文件
3. 生成相机参数配置文件

用法：python video2euroc.py <视频文件路径> [选项]
"""

import os
import sys
import argparse
import subprocess
import shutil
from tqdm import tqdm


def run_command(command, desc):
    """
    运行命令并显示进度
    """
    print(f"\n执行: {desc}")
    print(f"命令: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: 命令执行失败")
        print(f"详细信息: {e}")
        print(f"输出: {e.stdout}")
        print(f"错误: {e.stderr}")
        return False


def clean_output_directory(directory):
    """
    清空输出目录，如果目录存在则删除其中的内容，如果不存在则创建
    """
    # 获取目录的绝对路径
    abs_dir = os.path.abspath(directory)
    
    # 如果目录存在，删除它及其所有内容
    if os.path.exists(abs_dir):
        print(f"\n清空输出目录: {abs_dir}")
        shutil.rmtree(abs_dir)
    
    # 创建新的空目录
    os.makedirs(abs_dir, exist_ok=True)
    print(f"创建目录: {abs_dir}")
    return True


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="将视频转换为EuRoC格式的数据集")
    parser.add_argument("video_path", nargs='?', default="test.mp4", help="输入视频文件的路径 (默认: test.mp4)")
    parser.add_argument("--output-dir", "-o", default="main_folder/mav0/cam0/data",
                        help="图像输出目录路径 (默认: main_folder/mav0/cam0/data)")
    parser.add_argument("--timestamp-file", "-t", default="main_folder/mav0/timestamp.txt",
                        help="时间戳文件路径 (默认: main_folder/mav0/timestamp.txt)")
    parser.add_argument("--sensor-file", "-s", default="main_folder/mav0/sensor.yaml",
                        help="传感器配置文件路径 (默认: main_folder/mav0/sensor.yaml)")
    parser.add_argument("--fx", type=float, default=363.76489,
                        help="相机参数fx (默认: 363.76489)")
    parser.add_argument("--fy", type=float, default=363.76489,
                        help="相机参数fy (默认: 363.76489)")
    parser.add_argument("--cx", type=float, default=239.17206,
                        help="相机参数cx (默认: 239.17206)")
    parser.add_argument("--cy", type=float, default=173.14810,
                        help="相机参数cy (默认: 173.14810)")
    args = parser.parse_args()
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.join(script_dir, "tools")
    
    # 获取视频文件的绝对路径
    video_path = os.path.abspath(args.video_path)
    if not os.path.isfile(video_path):
        print(f"错误: 视频文件不存在 {video_path}")
        return 1
    
    print("\n===== 视频转EuRoC数据集工具 =====")
    print(f"视频文件: {video_path}")
    print(f"图像输出目录: {args.output_dir}")
    print(f"时间戳文件: {args.timestamp_file}")
    print(f"传感器配置文件: {args.sensor_file}")
    print(f"相机参数: fx={args.fx}, fy={args.fy}, cx={args.cx}, cy={args.cy}")
    
    # 清空输出目录
    output_base_dir = os.path.dirname(os.path.dirname(args.output_dir))
    if not clean_output_directory(output_base_dir):
        print(f"错误: 无法清空输出目录 {output_base_dir}")
        return 1
    
    # 步骤1: 从视频中提取帧
    video2frames_script = os.path.join(tools_dir, "video2frames.py")
    cmd1 = [
        sys.executable, video2frames_script, 
        video_path,
        "--output-dir", args.output_dir
    ]
    if not run_command(cmd1, "步骤1 - 从视频中提取帧"):
        return 1
    
    # 步骤2: 生成时间戳文件
    timestamp_script = os.path.join(tools_dir, "generate_timestamp.py")
    cmd2 = [
        sys.executable, timestamp_script,
        "--image-dir", args.output_dir,
        "--output-file", args.timestamp_file
    ]
    if not run_command(cmd2, "步骤2 - 生成时间戳文件"):
        return 1
    
    # 步骤3: 生成相机参数配置文件
    sensor_script = os.path.join(tools_dir, "generate_sensor_yaml.py")
    cmd3 = [
        sys.executable, sensor_script,
        "--fx", str(args.fx),
        "--fy", str(args.fy),
        "--cx", str(args.cx),
        "--cy", str(args.cy),
        "--output-file", args.sensor_file
    ]
    if not run_command(cmd3, "步骤3 - 生成相机参数配置文件"):
        return 1
    
    print("\n===== 处理完成 =====")
    print(f"EuRoC格式数据集已生成在: {os.path.dirname(os.path.dirname(args.output_dir))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())