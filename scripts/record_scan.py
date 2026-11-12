#!/usr/bin/env python3
"""Record three real LaserScan frames for the Lab3 filter comparison."""
import argparse
import json
import math
import statistics
import time
from datetime import datetime
from pathlib import Path

import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--label', required=True, choices=['A', 'B'])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--timeout', type=float, default=30)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    rclpy.init()
    node = rclpy.create_node('lab3_scan_recorder')
    samples = []
    last_sample = -math.inf

    def callback(msg):
        nonlocal last_sample
        now = time.monotonic()
        if now - last_sample < 1 or len(samples) >= 3:
            return
        last_sample = now
        row = {
            'sample': len(samples) + 1,
            'stamp_sec': msg.header.stamp.sec,
            'stamp_nanosec': msg.header.stamp.nanosec,
            'frame_id': msg.header.frame_id,
            'total': len(msg.ranges),
            'inf': sum(math.isinf(v) for v in msg.ranges),
            'nan': sum(math.isnan(v) for v in msg.ranges),
            'finite': sum(math.isfinite(v) for v in msg.ranges),
        }
        samples.append(row)
        print(json.dumps(row), flush=True)

    subscription = node.create_subscription(LaserScan, '/scan', callback, qos_profile_sensor_data)
    deadline = time.monotonic() + args.timeout
    try:
        while len(samples) < 3 and time.monotonic() < deadline:
            rclpy.spin_once(node, timeout_sec=0.2)
        result = {
            'label': args.label,
            'recorded_at': datetime.now().astimezone().isoformat(),
            'complete': len(samples) == 3,
            'samples': samples,
            'means': {key: statistics.mean(row[key] for row in samples)
                      for key in ('total', 'inf', 'nan', 'finite')} if samples else {},
        }
        args.output.expanduser().parent.mkdir(parents=True, exist_ok=True)
        args.output.expanduser().write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        if len(samples) != 3:
            raise SystemExit('Timed out before receiving 3 samples; check /scan, domain and driver.')
        print(json.dumps(result['means']), flush=True)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
