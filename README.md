# 视频转EuRoC数据集工具

这是一个将普通视频文件转换为EuRoC格式数据集的工具，可用于视觉SLAM算法的测试和评估。

## 功能介绍

该工具可以将视频文件转换为符合EuRoC数据集格式的结构，按顺序执行以下步骤：

1. 从视频中提取帧并按时间戳命名保存为图像文件
2. 生成包含图像时间戳信息的时间戳文件
3. 生成包含相机参数的配置文件

## 安装依赖

本工具依赖以下Python库：

```bash
pip install opencv-python tqdm
```

## 使用方法

### 基本用法

```bash
python video2euroc.py <视频文件路径>
```

### 示例

```bash
python video2euroc.py my_video.mp4
```

### 高级用法（自定义参数）

```bash
python video2euroc.py my_video.mp4 --output-dir custom_folder/mav0/cam0/data --raw-width 1920
```

## 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `video_path` | - | 输入视频文件的路径 | (必填) |
| `--output-dir` | `-o` | 图像输出目录路径 | `main_folder/mav0/cam0/data` |
| `--timestamp-file` | `-t` | 时间戳文件路径 | `main_folder/mav0/timestamp.txt` |
| `--sensor-file` | `-s` | 传感器配置文件路径 | `main_folder/mav0/sensor.yaml` |
| `--fx` | - | 相机参数fx | `363.76489` |
| `--fy` | - | 相机参数fy | `363.76489` |
| `--cx` | - | 相机参数cx | `239.17206` |
| `--cy` | - | 相机参数cy | `173.14810` |
| `--raw-width` | - | 原始视频宽度，用于缩放相机内参 | 不缩放 |

## 输出结构

转换后的数据集将按照以下结构组织：

```
main_folder/
  └── mav0/
      ├── cam0/
      │   └── data/
      │       ├── 0.png
      │       ├── 33333333.png
      │       ├── 66666666.png
      │       └── ...
      ├── timestamp.txt
      └── sensor.yaml
```

## 工具组件说明

### 1. video2euroc.py

主脚本，协调调用其他工具脚本完成整个转换流程。

### 2. tools/video2frames.py

视频帧提取工具，用于将视频分解为单独的帧，并按照时间戳命名保存。

- 功能：从视频中提取帧并调整尺寸（默认宽度为480像素）
- 输出：按纳秒级时间戳命名的PNG图像文件

注意，这个脚本会将图片压缩到480px宽度。

### 3. tools/generate_timestamp.py

时间戳文件生成工具，用于扫描图片目录，生成包含每个图片时间戳信息的文件。

- 功能：读取图片文件名中的时间戳，生成EuRoC格式的时间戳文件
- 输出：每行包含两个相同时间戳值的文本文件

### 4. tools/generate_sensor_yaml.py

相机参数配置文件生成工具，用于创建包含相机参数和ORB特征提取器参数的YAML文件。

- 功能：根据用户提供的相机内参生成配置文件
- 输出：包含相机参数和ORB特征提取器参数的YAML文件
- 自动检测：如果项目根目录下存在camera_matrix.csv和distortion_coefficients.csv文件，将优先从中读取相机参数

## 相机标定数据使用

本工具支持直接使用Matlab相机标定工具箱导出的标定数据。在项目根目录下放置以下文件可自动读取相机参数：

1. `camera_matrix.csv` - 包含相机内参矩阵
2. `distortion_coefficients.csv` - 包含畸变系数

### 从Matlab导出相机参数

在Matlab中使用以下代码从cameraParams对象导出相机参数：

```matlab
% 假设您已经有了cameraParams对象
% 提取内参矩阵
K = cameraParams.IntrinsicMatrix';  % 注意这里需要转置

% 提取畸变系数 (针对径向畸变和切向畸变)
distCoeffs = cameraParams.RadialDistortion;
if ~isempty(cameraParams.TangentialDistortion)
    distCoeffs = [distCoeffs, cameraParams.TangentialDistortion];
end

writematrix(K, 'camera_matrix.csv');
writematrix(distCoeffs, 'distortion_coefficients.csv');
```

导出后，将这两个文件放在项目根目录下，并使用`--raw-width`参数指定原始视频的宽度，工具会自动缩放相机参数以适应480px宽度的输出图像。