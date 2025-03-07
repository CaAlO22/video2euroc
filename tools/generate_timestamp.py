#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
时间戳文件生成工具

该脚本用于扫描图片目录，生成timestamp.txt文件，其中包含每个图片的时间戳信息。
用法：python generate_timestamp.py
"""

import os
import sys
import argparse
from tqdm import tqdm


def ensure_dir(directory):
    """
    确保目录存在，如果不存在则创建
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")


def generate_timestamp_file(image_dir, output_file):
    """
    生成时间戳文件
    """
    # 确保图片目录存在
    if not os.path.exists(image_dir):
        print(f"错误: 图片目录不存在 {image_dir}")
        return False

    # 获取所有PNG文件
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    if not image_files:
        print(f"错误: 目录中没有找到PNG文件 {image_dir}")
        return False

    # 提取时间戳并排序
    timestamps = []
    # 创建进度条
    pbar = tqdm(image_files, desc="处理图片文件", unit="个")
    for image_file in pbar:
        # 去除.png后缀
        timestamp = os.path.splitext(image_file)[0]
        try:
            # 验证时间戳是否为有效数字
            timestamp_value = int(timestamp)
            timestamps.append((timestamp, timestamp_value))
        except ValueError:
            print(f"警告: 跳过无效的文件名 {image_file}")
            continue
    
    # 关闭进度条
    pbar.close()

    # 按时间戳数值排序
    timestamps.sort(key=lambda x: x[1])

    # 创建输出目录（如果需要）
    output_dir = os.path.dirname(output_file)
    if output_dir:
        ensure_dir(output_dir)

    # 写入时间戳文件
    try:
        with open(output_file, 'w') as f:
            for timestamp, _ in timestamps:
                f.write(f"{timestamp} {timestamp}\n")
        print(f"成功生成时间戳文件: {output_file}")
        print(f"共处理 {len(timestamps)} 个图片文件")
        return True
    except IOError as e:
        print(f"错误: 无法写入文件 {output_file}")
        print(f"详细信息: {str(e)}")
        return False


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="生成图片时间戳文件")
    parser.add_argument("--image-dir", "-i", default="main_folder/mav0/cam0/data",
                        help="图片目录路径 (默认: main_folder/mav0/cam0/data)")
    parser.add_argument("--output-file", "-o", default="main_folder/mav0/timestamp.txt",
                        help="输出文件路径 (默认: main_folder/mav0/timestamp.txt)")
    args = parser.parse_args()

    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # 构建完整路径
    image_dir = os.path.join(project_root, args.image_dir)
    output_file = os.path.join(project_root, args.output_file)

    print(f"图片目录: {image_dir}")
    print(f"输出文件: {output_file}")

    # 生成时间戳文件
    success = generate_timestamp_file(image_dir, output_file)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())