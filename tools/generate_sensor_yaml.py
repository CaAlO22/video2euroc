#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
相机参数配置文件生成工具

该脚本用于在mav0目录下创建sensor.yaml文件，包含相机参数和ORB特征提取器参数。
用户可以自定义相机内参（fx, fy, cx, cy）或使用默认值。
如果项目根目录下存在camera_matrix.csv和distortion_coefficients.csv文件，将优先从中读取相机参数。
如果项目根目录下存在camera_calibration.yaml文件，将作为第二优先级读取。
用法：python generate_sensor_yaml.py [--fx 值] [--fy 值] [--cx 值] [--cy 值] [--raw-width 值]
"""

import os
import sys
import argparse
import yaml
import csv
import numpy as np


def ensure_dir(directory):
    """
    确保目录存在，如果不存在则创建
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"创建目录: {directory}")


def read_camera_matrix_csv(matrix_file, distortion_file, raw_width=None):
    """
    从CSV文件中读取相机矩阵和畸变系数
    
    参数：
        matrix_file: 相机矩阵CSV文件路径
        distortion_file: 畸变系数CSV文件路径
        raw_width: 原始视频宽度，用于缩放内参
        
    返回：
        dict: 包含fx, fy, cx, cy, k1, k2, p1, p2的字典，如果读取失败则返回None
    """
    try:
        if not os.path.exists(matrix_file):
            print(f"未找到相机矩阵文件: {matrix_file}")
            return None
            
        if not os.path.exists(distortion_file):
            print(f"未找到畸变系数文件: {distortion_file}")
            return None
            
        print(f"读取相机矩阵文件: {matrix_file}")
        print(f"读取畸变系数文件: {distortion_file}")
        
        # 读取相机矩阵
        camera_matrix = []
        with open(matrix_file, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                if row:  # 跳过空行
                    camera_matrix.append([float(x) for x in row])
        
        # 读取畸变系数
        distortion_coeffs = []
        with open(distortion_file, 'r') as f:
            csv_reader = csv.reader(f)
            for row in csv_reader:
                if row:  # 跳过空行
                    distortion_coeffs.append([float(x) for x in row])
        
        # 提取fx, fy, cx, cy
        fx = camera_matrix[0][0]
        fy = camera_matrix[1][1]
        cx = camera_matrix[0][2]
        cy = camera_matrix[1][2]
        
        # 提取畸变系数
        k1 = distortion_coeffs[0][0] if len(distortion_coeffs) > 0 and len(distortion_coeffs[0]) > 0 else 0.0
        k2 = distortion_coeffs[0][1] if len(distortion_coeffs) > 0 and len(distortion_coeffs[0]) > 1 else 0.0
        p1 = distortion_coeffs[0][2] if len(distortion_coeffs) > 0 and len(distortion_coeffs[0]) > 2 else 0.0
        p2 = distortion_coeffs[0][3] if len(distortion_coeffs) > 0 and len(distortion_coeffs[0]) > 3 else 0.0
        
        # 如果提供了原始宽度，则缩放内参
        if raw_width is not None and raw_width > 0:
            scale_factor = 480.0 / raw_width
            fx = fx * scale_factor
            fy = fy * scale_factor
            cx = cx * scale_factor
            cy = cy * scale_factor
            print(f"应用缩放因子: {scale_factor} (原始宽度: {raw_width}px, 目标宽度: 480px)")
        
        print(f"从CSV文件中读取相机参数:")
        print(f"  - fx: {fx}")
        print(f"  - fy: {fy}")
        print(f"  - cx: {cx}")
        print(f"  - cy: {cy}")
        print(f"  - k1: {k1}")
        print(f"  - k2: {k2}")
        print(f"  - p1: {p1}")
        print(f"  - p2: {p2}")
        
        return {'fx': fx, 'fy': fy, 'cx': cx, 'cy': cy, 'k1': k1, 'k2': k2, 'p1': p1, 'p2': p2}
    except Exception as e:
        print(f"读取CSV文件时出错: {str(e)}")
        return None


def read_camera_calibration(calib_file):
    """
    从相机标定文件中读取相机参数
    
    返回：
        dict: 包含fx, fy, cx, cy的字典，如果读取失败则返回None
    """
    try:
        if not os.path.exists(calib_file):
            print(f"未找到相机标定文件: {calib_file}")
            return None
            
        print(f"读取相机标定文件: {calib_file}")
        with open(calib_file, 'r') as f:
            calib_data = yaml.safe_load(f)
        
        # 从标定文件中提取相机矩阵
        if 'camera_matrix' in calib_data and 'data' in calib_data['camera_matrix']:
            matrix_data = calib_data['camera_matrix']['data']
            
            # 提取fx, fy, cx, cy
            fx = matrix_data[0][0]
            fy = matrix_data[1][1]
            cx = matrix_data[0][2]
            cy = matrix_data[1][2]
            
            print(f"从标定文件中读取相机参数:")
            print(f"  - fx: {fx}")
            print(f"  - fy: {fy}")
            print(f"  - cx: {cx}")
            print(f"  - cy: {cy}")
            
            return {'fx': fx, 'fy': fy, 'cx': cx, 'cy': cy}
        else:
            print(f"标定文件格式不正确，未找到相机矩阵数据")
            return None
    except Exception as e:
        print(f"读取标定文件时出错: {str(e)}")
        return None


def generate_sensor_yaml(output_file, fx=363.76489, fy=363.76489, cx=239.17206, cy=173.14810, k1=0.0, k2=0.0, p1=0.0, p2=0.0):
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

# 畸变参数
Camera.k1: {k1}
Camera.k2: {k2}
Camera.p1: {p1}
Camera.p2: {p2}

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
    parser.add_argument("--raw-width", type=int, default=None,
                        help="原始视频宽度(px)，用于缩放内参 (默认: 不缩放)")
    parser.add_argument("--output-file", "-o", default="main_folder/mav0/sensor.yaml",
                        help="输出文件路径 (默认: main_folder/mav0/sensor.yaml)")
    parser.add_argument("--calib-file", "-c", default=None,
                        help="相机标定文件路径 (默认: 项目根目录下的camera_calibration.yaml)")
    args = parser.parse_args()
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # 构建完整路径
    output_file = os.path.join(project_root, args.output_file)
    
    # 定义相机参数默认值
    fx = args.fx
    fy = args.fy
    cx = args.cx
    cy = args.cy
    k1 = 0.0
    k2 = 0.0
    p1 = 0.0
    p2 = 0.0
    
    # 首先尝试从CSV文件读取相机参数
    matrix_file = os.path.join(project_root, "camera_matrix.csv")
    distortion_file = os.path.join(project_root, "distortion_coefficients.csv")
    csv_params = read_camera_matrix_csv(matrix_file, distortion_file, args.raw_width)
    
    if csv_params:
        fx = csv_params['fx']
        fy = csv_params['fy']
        cx = csv_params['cx']
        cy = csv_params['cy']
        k1 = csv_params['k1']
        k2 = csv_params['k2']
        p1 = csv_params['p1']
        p2 = csv_params['p2']
        print(f"使用CSV文件中的相机参数")
    else:
        # 如果CSV文件不存在或读取失败，尝试从标定文件读取相机参数
        calib_file = os.path.join(project_root, "camera_calibration.yaml") if not args.calib_file else os.path.join(project_root, args.calib_file)
        camera_params = read_camera_calibration(calib_file)
        
        # 如果成功读取标定文件，使用其中的参数，否则使用命令行参数或默认值
        if camera_params:
            fx = camera_params['fx']
            fy = camera_params['fy']
            cx = camera_params['cx']
            cy = camera_params['cy']
            print(f"使用标定文件中的相机参数")
        else:
            print(f"使用命令行参数或默认值:")
            print(f"  - fx: {fx}")
            print(f"  - fy: {fy}")
            print(f"  - cx: {cx}")
            print(f"  - cy: {cy}")
    
    print(f"输出文件: {output_file}")
    
    # 生成sensor.yaml文件
    success = generate_sensor_yaml(output_file, fx, fy, cx, cy, k1, k2, p1, p2)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())