import numpy as np
from scipy.io import wavfile
import json

# 1. 你的最新 AHAP 數據
ahap_data = {
    "Version": 1.0,
    "Metadata": {
        "Project": "BadgeAnimation",
        "Description": "Tap, long float up, peak transient, and a new long tail vibration with a pause."
    },
    "Pattern": [
        {
            "Event": {
                "Time": 0.6,
                "EventType": "HapticContinuous",
                "EventDuration": 0.8,
                "EventParameters": [
                    {"ParameterID": "HapticIntensity", "ParameterValue": 1.0},
                    {"ParameterID": "HapticSharpness", "ParameterValue": 0.2}
                ]
            }
        },
        {
            "ParameterCurve": {
                "ParameterID": "HapticIntensityControl",
                "Time": 0.6,
                "ParameterCurveControlPoints": [
                    {"Time": 0.0, "ParameterValue": 0.0},
                    {"Time": 0.4, "ParameterValue": 0.3},
                    {"Time": 0.7, "ParameterValue": 0.8},
                    {"Time": 0.8, "ParameterValue": 1.0}
                ]
            }
        },
        {
            "Event": {
                "Time": 2.4,
                "EventType": "HapticContinuous",
                "EventDuration": 0.1,
                "EventParameters": [
                    {"ParameterID": "HapticIntensity", "ParameterValue": 0.8},
                    {"ParameterID": "HapticSharpness", "ParameterValue": 0.5}
                ]
            }
        },
        {
            "ParameterCurve": {
                "ParameterID": "HapticIntensityControl",
                "Time": 2.1,
                "ParameterCurveControlPoints": [
                    {"Time": 0.0, "ParameterValue": 1.0},
                    {"Time": 0.7, "ParameterValue": 0.5},
                    {"Time": 1.0, "ParameterValue": 0.0}
                ]
            }
        }
    ]
}

sample_rate = 44100

# 2. 準確計算總長度 (以 Event 為主，因為 Curve 不能超越 Event 的生命週期)
max_time = 0.0
for item in ahap_data.get('Pattern', []):
    if 'Event' in item:
        event_end = item['Event']['Time'] + item['Event'].get('EventDuration', 0.02)
        if event_end > max_time:
            max_time = event_end

total_duration = max_time + 0.5
t = np.linspace(0, total_duration, int(sample_rate * total_duration), endpoint=False)

# 初始化陣列
envelope = np.zeros_like(t)
frequency_map = np.full_like(t, 55.0)  # 預設頻率 55Hz
active_mask = np.zeros_like(t, dtype=bool)  # 記錄哪裡有震動正在發生

# 3. 第一步：解析 Event 的基礎強度、頻率 (Sharpness) 與生命週期
for item in ahap_data.get('Pattern', []):
    if 'Event' in item:
        event = item['Event']
        start_time = event['Time']

        # 判斷持續時間
        if event['EventType'] == 'HapticContinuous':
            dur = event['EventDuration']
        else:  # HapticTransient
            dur = 0.02

        start_idx = int(start_time * sample_rate)
        end_idx = int((start_time + dur) * sample_rate)
        end_idx = min(end_idx, len(envelope))

        # 標記這段時間為 active (這段時間內才會有聲音)
        active_mask[start_idx:end_idx] = True

        # 讀取 Intensity 和 Sharpness
        intensity = 1.0
        sharpness = 0.5
        for param in event.get('EventParameters', []):
            if param['ParameterID'] == 'HapticIntensity':
                intensity = param['ParameterValue']
            elif param['ParameterID'] == 'HapticSharpness':
                sharpness = param['ParameterValue']

        envelope[start_idx:end_idx] = intensity

        # 簡單映射：Sharpness 0~1 映射到 40Hz ~ 120Hz，模擬震動的「脆度」
        freq = 40 + (sharpness * 80)
        frequency_map[start_idx:end_idx] = freq

# 4. 第二步：解析 ParameterCurve，並與 Event 結合
for item in ahap_data.get('Pattern', []):
    if 'ParameterCurve' in item:
        curve = item['ParameterCurve']
        curve_start = curve['Time']
        points = curve['ParameterCurveControlPoints']

        for i in range(len(points) - 1):
            p1 = points[i]
            p2 = points[i + 1]

            t1 = p1['Time'] + curve_start
            t2 = p2['Time'] + curve_start
            v1 = p1['ParameterValue']
            v2 = p2['ParameterValue']

            idx1 = int(t1 * sample_rate)
            idx2 = int(t2 * sample_rate)

            # 確保不會超出陣列範圍
            idx1 = max(0, min(idx1, len(envelope)))
            idx2 = max(0, min(idx2, len(envelope)))

            if idx2 > idx1:
                # 產生漸變曲線，並與 envelope 相乘 (模擬 modulation)
                curve_segment = np.linspace(v1, v2, idx2 - idx1)
                envelope[idx1:idx2] = curve_segment * envelope[idx1:idx2]

# 將沒有 Event active 的地方歸零 (強行切斷無效的 Curve)
envelope[~active_mask] = 0.0

# 5. 生成動態頻率的正弦波 (利用積分計算瞬時相位，讓頻率變化更滑順)
phase = np.cumsum(2 * np.pi * frequency_map / sample_rate)
carrier_wave = np.sin(phase)

# 合成並輸出
audio_out = carrier_wave * envelope
audio_out = (audio_out * 32767).astype(np.int16)

file_name = "Test03_Custom_Haptic.wav"
wavfile.write(file_name, sample_rate, audio_out)

print(f"成功！已生成音檔: {file_name}")