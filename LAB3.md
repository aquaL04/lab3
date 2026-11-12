# Lab3 二维激光雷达实验

个人仓库：https://gitee.com/chuguoqing001/ai_lab

上游源码：https://gitee.com/yapengshi/lidar_pkg_ros2

## 配置

- ROS 2 Humble，工作空间 `~/ros2_ws`，包名 `lidar_pkg`。
- 下午实验使用 `ROS_DOMAIN_ID=12`。上午改为 11，晚上改为 13。
- `frame_id: laser`，与配套 URDF 保持一致。
- B 组滤波使用 `enabled: true`、`radius: 0.10`、`min_neighbors: 2`。
- `port_name: /dev/ttyACM0` 为课程示例值。本次准备阶段尚未接入雷达，接入后必须核对实际设备名再修改，不能作为已实测端口。

## 编译与启动

```bash
# 先退出所有 Conda 环境，确认 which python3 为 /usr/bin/python3
source /opt/ros/humble/setup.bash
export ROS_DOMAIN_ID=12
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
ros2 launch lidar_pkg monitor.launch.py
```

无桌面时使用 `ros2 launch lidar_pkg lidar.launch.py`。两种启动方式只运行一种。

## 滤波对照记录

保持雷达位置、目标、RViz 视角与尺度不变。先设 `filter.enabled: false`，启动后在另一终端执行：

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
export ROS_DOMAIN_ID=12
/usr/bin/python3 ~/ros2_ws/src/lidar_pkg_ros2/scripts/record_scan.py --label A --output ~/lab3_records/scan_A.json
```

保存 A 组 RViz 截图，停止驱动，再设 `filter.enabled: true`、`radius: 0.10`、`min_neighbors: 2`，使用同一命令重新启动，记录 B 组：

```bash
/usr/bin/python3 ~/ros2_ws/src/lidar_pkg_ros2/scripts/record_scan.py --label B --output ~/lab3_records/scan_B.json
```

脚本默认间隔 1 秒采集 3 帧，记录总点数、inf、NaN、有限值数量和均值。点数来自实际消息长度，不假设固定为 720。`grep -c inf` 统计的是匹配行数，不能可靠代表一行数组内的 inf 元素数量。

修改 YAML 后必须重启驱动。当前驱动在启动时读取参数。

## Git 记录

本仓库仅提交功能包，不提交整个工作空间。保留上游历史，`upstream` 指向课程仓库，`origin` 指向个人仓库。提交身份使用当前仓库本地配置；可用以下命令检查来源：

```bash
git config --show-origin --get user.name
git config --show-origin --get user.email
git status
git diff
git remote -v
git log -1
```

硬件接入后的端口、/scan 频率、A/B 有效点数与截图需要通过实测补充。
