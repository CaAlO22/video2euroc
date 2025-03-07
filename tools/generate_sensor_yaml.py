#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
相机参数配置文件生成工具

该脚本用于在mav0目录下创建sensor.yaml文件，包含相机参数和ORB特征提取器参数。
用户可以自定义相机内参（fx, fy, cx, cy）或使用默认值。
用法：python generate_sensor_yaml.py [--fx 值] [--fy 值] [--cx 值] [--cy 值]
"""

import os
import sys
import argparse


def ensure_dir(directory):
    """
    确保目录存在，如果不存在则创建
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")


def generate_sensor_yaml(output_file, fx=363.76489, fy=363.76489, cx=239.17206, cy=173.14810):
    """
    生成sensor.yaml文件
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir:
        ensure_dir(output_dir)
    
    # 准备YAML内容
    yaml_content = f"""%YAML:1.0

#--------------------------------------------------------------------------------------------
# Camera Parameters
#--------------------------------------------------------------------------------------------
Camera.type: "PinHole"

# Camera calibration and distortion parameters (OpenCV) 
Camera.fx: {fx}
Camera.fy: {fy}
Camera.cx: {cx}
Camera.cy: {cy}

# 畸变参数 (如果没有具体值，可以先设为0)
Camera.k1: 0.0
Camera.k2: 0.0
Camera.p1: 0.0
Camera.p2: 0.0

# Camera resolution (根据您的图像设置，这里使用估计值)
Camera.width: 480
Camera.height: 360

# Camera frames per second 
Camera.fps: 20.0

# Color order of the images (0: BGR, 1: RGB. It is ignored if images are grayscale)
Camera.RGB: 1

#--------------------------------------------------------------------------------------------
# ORB Parameters
#--------------------------------------------------------------------------------------------
# ORB Extractor: Number of features per image
ORBextractor.nFeatures: 1000

# ORB Extractor: Scale factor between levels in the scale pyramid 
ORBextractor.scaleFactor: 1.2

# ORB Extractor: Number of levels in the scale pyramid 
ORBextractor.nLevels: 8

# ORB Extractor: Fast threshold
# Image is divided in a grid. At each cell FAST are extracted imposing a minimum response.
# Firstly we impose iniThFAST. If no corners are detected we impose a lower value minThFAST
# You can lower these values if your images have low contrast
ORBextractor.iniThFAST: 20
ORBextractor.minThFAST: 7

#--------------------------------------------------------------------------------------------
# Viewer Parameters
#--------------------------------------------------------------------------------------------
Viewer.KeyFrameSize: 0.05
Viewer.KeyFrameLineWidth: 1
Viewer.GraphLineWidth: 0.9
Viewer.PointSize: 2
Viewer.CameraSize: 0.08
Viewer.CameraLineWidth: 3
Viewer.ViewpointX: 0
Viewer.ViewpointY: -0.7
Viewer.ViewpointZ: -1.8
Viewer.ViewpointF: 500
"""
    
    # 写入文件
    try:
        with open(output_file, 'w') as f:
            f.write(yaml_content)
        print(f"成功生成sensor.yaml文件: {output_file}")
        return True
    except IOError as e:
        print(f"错误: 无法写入文件 {output_file}")
        print(f"详细信息: {str(e)}")
        return False


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="生成相机参数配置文件(sensor.yaml)")
    parser.add_argument("--fx", type=float, default=363.76489,
                        help="相机参数fx (默认: 363.76489)")
    parser.add_argument("--fy", type=float, default=363.76489,
                        help="相机参数fy (默认: 363.76489)")
    parser.add_argument("--cx", type=float, default=239.17206,
                        help="相机参数cx (默认: 239.17206)")
    parser.add_argument("--cy", type=float, default=173.14810,
                        help="相机参数cy (默认: 173.14810)")
    parser.add_argument("--output-file", "-o", default="main_folder/mav0/sensor.yaml",
                        help="输出文件路径 (默认: main_folder/mav0/sensor.yaml)")
    args = parser.parse_args()
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # 构建完整路径
    output_file = os.path.join(project_root, args.output_file)
    
    print(f"相机参数:")
    print(f"  - fx: {args.fx}")
    print(f"  - fy: {args.fy}")
    print(f"  - cx: {args.cx}")
    print(f"  - cy: {args.cy}")
    print(f"输出文件: {output_file}")
    
    # 生成sensor.yaml文件
    success = generate_sensor_yaml(output_file, args.fx, args.fy, args.cx, args.cy)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())