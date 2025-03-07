# 单目相机标定工具

## 功能介绍

该工具可以接收相机拍摄的棋盘格视频，并进行相机标定，按顺序执行以下步骤：

1. 从视频中提取帧
2. 检测棋盘格角点
3. 计算相机内参和畸变系数
4. 保存标定结果并可视化

## 环境要求

- Python 3.6+
- OpenCV
- NumPy
- Matplotlib
- PyYAML
- tqdm

## 使用方法

### 基本用法

```bash
python camera_calibration.py <视频文件路径>
```

### 高级用法（自定义参数）

```bash
python camera_calibration.py my_video.mp4 --board-size 8x6 --square-size 25.0 --max-frames 40
```

## 参数说明

| 参数 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `video_path` | - | 输入视频文件的路径 | (必填) |
| `--output-dir` | `-o` | 输出目录路径 | `calibration_results` |
| `--frames-dir` | `-f` | 帧提取目录路径 | `<output_dir>/frames` |
| `--calib-file` | `-c` | 标定结果文件路径 | `<output_dir>/camera_calibration.yaml` |
| `--board-size` | `-b` | 棋盘格内角点数量，格式为'宽x高' | `9x6` |
| `--square-size` | `-s` | 棋盘格方格实际尺寸，单位为毫米 | `20.0` |
| `--max-frames` | `-m` | 用于标定的最大帧数 | `30` |
| `--no-visualize` | - | 不生成可视化结果 | `False` |

## 标定结果

标定完成后，将在指定的输出目录中生成以下内容：

1. `frames/` - 从视频中提取的帧
2. `camera_calibration.yaml` - 相机标定参数文件，包含相机矩阵和畸变系数
3. `visualization/` - 可视化结果目录
   - `corners_*.png` - 检测到棋盘格角点的图像
   - `undistorted.png` - 校正后的图像
   - `comparison.png` - 原始图像与校正后图像的对比

## 标定参数文件格式

标定结果保存为YAML格式，包含以下内容：

```yaml
camera_matrix:
  rows: 3
  cols: 3
  data:
  - [fx, 0, cx]
  - [0, fy, cy]
  - [0, 0, 1]
distortion_coefficients:
  rows: 1
  cols: 5
  data:
  - [k1, k2, p1, p2, k3]
image_width: 宽度
image_height: 高度
reprojection_error: 重投影误差
```

## 使用建议

1. 棋盘格视频拍摄建议：
   - 确保棋盘格在视频中完全可见
   - 从不同角度拍摄棋盘格，覆盖整个视野
   - 保持光照均匀，避免反光
   - 尽量使棋盘格占据画面的大部分区域

2. 参数设置建议：
   - 正确设置棋盘格内角点数量（`--board-size`）
   - 准确测量并设置方格实际尺寸（`--square-size`）
   - 如果视频较长，可以适当增加最大帧数（`--max-frames`）

## 示例

```bash
# 基本用法
python camera_calibration.py chessboard_video.mp4

# 自定义棋盘格尺寸和方格大小
python camera_calibration.py chessboard_video.mp4 --board-size 7x5 --square-size 30.0

# 指定输出目录和最大帧数
python camera_calibration.py chessboard_video.mp4 --output-dir my_calibration --max-frames 50
```