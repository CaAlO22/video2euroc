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
python video2euroc.py my_video.mp4 --output-dir custom_folder/mav0/cam0/data --fx 450.0 --fy 450.0
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

### 3. tools/generate_timestamp.py

时间戳文件生成工具，用于扫描图片目录，生成包含每个图片时间戳信息的文件。

- 功能：读取图片文件名中的时间戳，生成EuRoC格式的时间戳文件
- 输出：每行包含两个相同时间戳值的文本文件

### 4. tools/generate_sensor_yaml.py

相机参数配置文件生成工具，用于创建包含相机参数和ORB特征提取器参数的YAML文件。

- 功能：根据用户提供的相机内参生成配置文件
- 输出：包含相机参数和ORB特征提取器参数的YAML文件

## 注意事项

1. 输入视频应当稳定，避免剧烈抖动，以便于SLAM算法处理
2. 默认相机参数可能需要根据实际相机进行调整
3. 生成的数据集默认分辨率为480x360像素
4. 时间戳以纳秒为单位

## 常见问题

**Q: 如何获取相机的内参？**

A: 可以使用OpenCV的相机标定功能获取相机内参，或参考相机厂商提供的参数。

**Q: 生成的数据集可以用于哪些SLAM系统？**

A: 生成的数据集符合EuRoC格式，可用于ORB-SLAM、VINS-Fusion等常见视觉SLAM系统。

**Q: 如何调整输出图像的分辨率？**

A: 可以修改`tools/video2frames.py`中的`resize_image`函数的`target_width`参数。