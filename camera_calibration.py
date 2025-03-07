#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
单目相机标定工具

该脚本用于接收相机拍摄的棋盘格视频，并进行相机标定，按顺序执行以下步骤：
1. 从视频中提取帧
2. 检测棋盘格角点
3. 计算相机内参和畸变系数
4. 保存标定结果并可视化

用法：python camera_calibration.py <视频文件路径> [选项]
"""

import os
import sys
import cv2
import numpy as np
import argparse
import subprocess
import shutil
from tqdm import tqdm
import yaml
import glob
import matplotlib.pyplot as plt


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


def extract_frames(video_path, output_dir, max_frames=None):
    """
    从视频中提取帧用于标定
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
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
    
    # 如果指定了最大帧数，则计算采样间隔
    if max_frames and frame_count > max_frames:
        frame_interval = frame_count // max_frames
        print(f"  - 采样间隔: 每 {frame_interval} 帧提取一帧")
    else:
        frame_interval = 1
    
    # 提取帧
    frame_index = 0
    saved_count = 0
    success = True
    
    # 创建进度条
    pbar = tqdm(
        total=frame_count,
        desc="提取帧",
        unit="帧",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
        postfix={"已保存": 0, "当前帧": 0},
        dynamic_ncols=True
    )
    
    while success:
        # 读取下一帧
        success, frame = video.read()
        
        if success:
            # 只保存符合采样间隔的帧
            if frame_index % frame_interval == 0:
                # 保存帧为PNG文件
                output_path = os.path.join(output_dir, f"frame_{saved_count:04d}.png")
                cv2.imwrite(output_path, frame)
                saved_count += 1
            
            # 更新进度条
            frame_index += 1
            pbar.set_postfix({"已保存": saved_count, "当前帧": frame_index})
            pbar.update(1)
    
    # 关闭进度条和视频
    pbar.close()
    video.release()
    
    print(f"\n完成! 共提取 {saved_count} 帧到 {output_dir}")
    return saved_count > 0


def calibrate_camera(image_dir, board_size, square_size, output_file, visualize=True):
    """
    使用棋盘格图像进行相机标定
    """
    # 准备对象点，如(0,0,0), (1,0,0), (2,0,0) ..., (8,5,0)
    objp = np.zeros((board_size[0] * board_size[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:board_size[0], 0:board_size[1]].T.reshape(-1, 2)
    
    # 将对象点乘以方格实际尺寸（毫米）
    objp = objp * square_size
    
    # 存储对象点和图像点的数组
    objpoints = []  # 3D点在真实世界中的坐标
    imgpoints = []  # 2D点在图像平面上的坐标
    
    # 获取图像列表
    images = glob.glob(os.path.join(image_dir, '*.png'))
    if not images:
        print(f"错误: 在 {image_dir} 中未找到图像文件")
        return False
    
    # 图像尺寸
    img_size = None
    
    # 成功检测到角点的图像数量
    successful_detections = 0
    
    print(f"\n开始处理 {len(images)} 张图像进行标定...")
    
    # 创建进度条
    pbar = tqdm(
        total=len(images),
        desc="检测角点",
        unit="图像",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]",
        postfix={"成功": 0},
        dynamic_ncols=True
    )
    
    # 处理每张图像
    for fname in images:
        # 读取图像
        img = cv2.imread(fname)
        if img is None:
            pbar.update(1)
            continue
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 保存图像尺寸
        if img_size is None:
            img_size = (gray.shape[1], gray.shape[0])
        
        # 查找棋盘格角点
        ret, corners = cv2.findChessboardCorners(gray, board_size, None)
        
        # 如果找到角点，添加对象点和图像点
        if ret:
            # 细化角点位置
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
            
            objpoints.append(objp)
            imgpoints.append(corners2)
            
            successful_detections += 1
            
            # 如果需要可视化，绘制并显示角点
            if visualize:
                # 创建输出目录
                vis_dir = os.path.join(os.path.dirname(output_file), "visualization")
                os.makedirs(vis_dir, exist_ok=True)
                
                # 绘制角点
                cv2.drawChessboardCorners(img, board_size, corners2, ret)
                
                # 保存带有角点的图像
                base_name = os.path.basename(fname)
                vis_path = os.path.join(vis_dir, f"corners_{base_name}")
                cv2.imwrite(vis_path, img)
        
        pbar.set_postfix({"成功": successful_detections})
        pbar.update(1)
    
    pbar.close()
    
    if successful_detections == 0:
        print("错误: 未能在任何图像中检测到棋盘格角点")
        return False
    
    print(f"\n在 {successful_detections}/{len(images)} 张图像中成功检测到棋盘格角点")
    
    print("\n计算相机标定参数...")
    # 执行相机标定
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
        objpoints, imgpoints, img_size, None, None
    )
    
    # 计算重投影误差
    mean_error = 0
    for i in range(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
        error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
        mean_error += error
    
    mean_error /= len(objpoints)
    
    # 输出标定结果
    print(f"\n标定完成!")
    print(f"相机矩阵:\n{mtx}")
    print(f"畸变系数: {dist.ravel()}")
    print(f"平均重投影误差: {mean_error}")
    
    # 保存标定结果
    calibration_result = {
        'camera_matrix': {
            'rows': 3,
            'cols': 3,
            'data': mtx.tolist()
        },
        'distortion_coefficients': {
            'rows': 1,
            'cols': 5,
            'data': dist.ravel().tolist()
        },
        'image_width': img_size[0],
        'image_height': img_size[1],
        'reprojection_error': float(mean_error)
    }
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # 保存为YAML文件
    with open(output_file, 'w') as f:
        yaml.dump(calibration_result, f, default_flow_style=False)
    
    print(f"标定结果已保存到: {output_file}")
    
    # 如果需要可视化，显示校正效果
    if visualize and successful_detections > 0:
        # 选择一张图像进行可视化
        img = cv2.imread(images[0])
        h, w = img.shape[:2]
        
        # 获取新的相机矩阵
        newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        
        # 校正图像
        dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
        
        # 裁剪图像
        x, y, w, h = roi
        if all(v > 0 for v in [x, y, w, h]):
            dst = dst[y:y+h, x:x+w]
        
        # 保存校正后的图像
        vis_dir = os.path.join(os.path.dirname(output_file), "visualization")
        os.makedirs(vis_dir, exist_ok=True)
        undistorted_path = os.path.join(vis_dir, "undistorted.png")
        cv2.imwrite(undistorted_path, dst)
        
        # 创建对比图
        plt.figure(figsize=(12, 6))
        plt.subplot(121)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.title('原始图像')
        plt.axis('off')
        
        plt.subplot(122)
        plt.imshow(cv2.cvtColor(dst, cv2.COLOR_BGR2RGB))
        plt.title('校正后图像')
        plt.axis('off')
        
        # 保存对比图
        comparison_path = os.path.join(vis_dir, "comparison.png")
        plt.savefig(comparison_path)
        print(f"校正效果对比图已保存到: {comparison_path}")
    
    return True


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="单目相机标定工具")
    parser.add_argument("video_path", nargs='?', default="test.mp4", help="输入视频文件的路径 (默认: test.mp4)")
    parser.add_argument("--output-dir", "-o", default="calibration_results",
                        help="输出目录路径 (默认: calibration_results)")
    parser.add_argument("--frames-dir", "-f", default=None,
                        help="帧提取目录路径 (默认: <output_dir>/frames)")
    parser.add_argument("--calib-file", "-c", default=None,
                        help="标定结果文件路径 (默认: <output_dir>/camera_calibration.yaml)")
    parser.add_argument("--board-size", "-b", default="9x6",
                        help="棋盘格内角点数量，格式为'宽x高' (默认: 9x6)")
    parser.add_argument("--square-size", "-s", type=float, default=20.0,
                        help="棋盘格方格实际尺寸，单位为毫米 (默认: 20.0mm)")
    parser.add_argument("--max-frames", "-m", type=int, default=30,
                        help="用于标定的最大帧数 (默认: 30)")
    parser.add_argument("--no-visualize", action="store_true",
                        help="不生成可视化结果")
    args = parser.parse_args()
    
    # 获取视频文件的绝对路径
    video_path = os.path.abspath(args.video_path)
    if not os.path.isfile(video_path):
        print(f"错误: 视频文件不存在 {video_path}")
        return 1
    
    # 设置输出目录
    output_dir = os.path.abspath(args.output_dir)
    
    # 设置帧提取目录
    if args.frames_dir is None:
        frames_dir = os.path.join(output_dir, "frames")
    else:
        frames_dir = os.path.abspath(args.frames_dir)
    
    # 设置标定结果文件路径
    if args.calib_file is None:
        calib_file = os.path.join(output_dir, "camera_calibration.yaml")
    else:
        calib_file = os.path.abspath(args.calib_file)
    
    # 解析棋盘格尺寸
    try:
        board_width, board_height = map(int, args.board_size.split('x'))
        board_size = (board_width, board_height)
    except ValueError:
        print(f"错误: 棋盘格尺寸格式不正确 '{args.board_size}'，应为'宽x高'，例如'9x6'")
        return 1
    
    print("\n===== 单目相机标定工具 =====")
    print(f"视频文件: {video_path}")
    print(f"输出目录: {output_dir}")
    print(f"帧提取目录: {frames_dir}")
    print(f"标定结果文件: {calib_file}")
    print(f"棋盘格尺寸: {board_size[0]}x{board_size[1]} 内角点")
    print(f"方格尺寸: {args.square_size} 毫米")
    print(f"最大帧数: {args.max_frames}")
    print(f"生成可视化: {'否' if args.no_visualize else '是'}")
    
    # 清空输出目录
    if not clean_output_directory(output_dir):
        print(f"错误: 无法清空输出目录 {output_dir}")
        return 1
    
    # 步骤1: 从视频中提取帧
    print("\n===== 步骤1: 从视频中提取帧 =====")
    if not extract_frames(video_path, frames_dir, args.max_frames):
        print(f"错误: 从视频中提取帧失败")
        return 1
    
    # 步骤2: 检测棋盘格角点并计算相机参数
    print("\n===== 步骤2: 检测棋盘格角点并计算相机参数 =====")
    if not calibrate_camera(frames_dir, board_size, args.square_size, calib_file, not args.no_visualize):
        print(f"错误: 相机标定失败")
        return 1
    
    print("\n===== 处理完成 =====")
    print(f"相机标定结果已保存到: {calib_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())