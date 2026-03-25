import numpy as np
import scipy.io.wavfile as wav
import scipy.ndimage as ndimage
import os

# --- 基礎參數 ---
FREQUENCY = 200  # 頻率 (Hz)
SAMPLE_RATE = 48000  # 取樣率
OUTPUT_FOLDER = "Vibration_Interactive_v6"  # 資料夾名稱

# 建立輸出資料夾
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)


# ===========================
#      工具函式
# ===========================

def generate_sine_wave(duration_ms):
    """產生純淨的正弦波基底"""
    num_samples = int((duration_ms / 1000) * SAMPLE_RATE)
    if num_samples == 0: return np.array([]), 0
    t = np.linspace(0, duration_ms / 1000, num_samples, endpoint=False)
    base_wave = np.sin(2 * np.pi * FREQUENCY * t)
    return base_wave, num_samples


def save_wav(filename, audio_data):
    """將數據存為 WAV 檔"""
    # 確保數據在 -1 到 1 之間
    audio_data = np.clip(audio_data, -1.0, 1.0)
    audio_int16 = (audio_data * 32767).astype(np.int16)
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    wav.write(filepath, SAMPLE_RATE, audio_int16)
    print(f"✅ 檔案已輸出: {filepath}")


# ===========================
#      模式 1: 正常震動
# ===========================

def mode_normal():
    print("\n--- 進入 [正常模式] ---")
    try:
        ms = int(input("請輸入長度 (ms) [例如 200]: "))
        intensity_input = float(input("請輸入強度 (0 ~ 100) [例如 90]: "))
        intensity = intensity_input / 100.0

        base_wave, num_samples = generate_sine_wave(ms)
        audio = base_wave * intensity

        # 前後淡入淡出 (避免啵啵聲)
        fade_samples = int((2 / 1000) * SAMPLE_RATE)
        if num_samples > 2 * fade_samples:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            audio[:fade_samples] *= fade_in
            audio[-fade_samples:] *= fade_out

        filename = f"Normal_{ms}ms_Vol{int(intensity_input)}.wav"
        save_wav(filename, audio)
    except ValueError:
        print("❌ 輸入錯誤")


# ===========================
#      模式 2: 多段自訂
# ===========================

def mode_advanced_segments():
    print("\n--- 進入 [多段自訂模式] ---")
    print("說明：請依照順序輸入每一段的 '時間' 與 '目標強度'。")
    print("格式範例：100,30; 200,30; 100,100; 100,0")

    try:
        input_str = input("\n請輸入設定字串: ")
        # 移除空格並用分號切割
        segments = input_str.replace(" ", "").split(';')

        time_points = [0]
        intensity_points = [0.0]
        current_time_ms = 0

        for seg in segments:
            if not seg: continue
            parts = seg.split(',')
            if len(parts) != 2:
                print(f"⚠️ 格式錯誤跳過: {seg}")
                continue

            dur = float(parts[0])
            target_vol = float(parts[1]) / 100.0

            current_time_ms += dur
            time_points.append(current_time_ms)
            intensity_points.append(target_vol)

        total_ms = time_points[-1]
        if total_ms <= 0:
            print("❌ 總長度為 0，無法產生。")
            return

        base_wave, total_samples = generate_sine_wave(total_ms)

        # 製作包絡線
        x_points = np.array(time_points) / 1000 * SAMPLE_RATE
        y_points = np.array(intensity_points)
        x_target = np.arange(total_samples)
        envelope = np.interp(x_target, x_points, y_points)

        audio = base_wave * envelope

        filename_clean = input_str.replace(" ", "").replace(",", "_").replace(";", "-")
        if len(filename_clean) > 30: filename_clean = "Advanced_Sequence"
        filename = f"{filename_clean}_{int(total_ms)}ms.wav"
        save_wav(filename, audio)

    except ValueError:
        print("❌ 數值格式錯誤。")


# ===========================
#      模式 3: 分析
# ===========================

def mode_analyze_sequence():
    print("\n--- 進入 [WAV 序列分析模式] ---")
    files = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".wav")]
    if not files:
        print(f"❌ 資料夾 {OUTPUT_FOLDER} 內沒有 WAV 檔案。")
        return

    print("請選擇要分析的檔案：")
    for idx, f in enumerate(files):
        print(f"{idx + 1}. {f}")

    try:
        selection = int(input("請輸入編號: ")) - 1
        if selection < 0 or selection >= len(files): return

        target_file = os.path.join(OUTPUT_FOLDER, files[selection])
        sr, data = wav.read(target_file)
        if len(data.shape) > 1: data = data[:, 0]

        # 分析邏輯 (簡化顯示)
        abs_data = np.abs(data.astype(np.float32) / 32768.0)
        THRESHOLD = 0.05
        is_active = abs_data > THRESHOLD

        # 簡單計算總長度與最大強度
        file_ms = (len(data) / sr) * 1000
        max_vol = np.max(abs_data) * 100

        print(f"\n📊 檔案: {files[selection]}")
        print(f"⏱️  總長: {file_ms:.1f} ms | 最大強度: {max_vol:.1f}")
        print("-" * 30)

    except Exception as e:
        print(f"❌ 錯誤: {e}")


# ===========================
#      模式 4: 快速生成 (新功能)
# ===========================

def mode_quick_generate():
    print("\n--- 進入 [快速生成模式] ---")
    print("說明：請輸入 '長度' 與 '強度'，用空格或逗號隔開。")
    print("範例：200 100  (代表 200ms, 強度100)")

    try:
        raw_input = input("請輸入數值: ")
        # 將逗號替換為空格，並分割字串
        parts = raw_input.replace(',', ' ').split()

        if len(parts) < 2:
            print("❌ 格式錯誤，請至少輸入兩個數字 (長度 強度)")
            return

        ms = int(parts[0])
        intensity_val = float(parts[1])
        intensity = intensity_val / 100.0

        # 1. 產生波形
        base_wave, num_samples = generate_sine_wave(ms)
        audio = base_wave * intensity

        # 2. 淡入淡出 (保護馬達)
        fade_samples = int((2 / 1000) * SAMPLE_RATE)
        if num_samples > 2 * fade_samples:
            fade_in = np.linspace(0, 1, fade_samples)
            fade_out = np.linspace(1, 0, fade_samples)
            audio[:fade_samples] *= fade_in
            audio[-fade_samples:] *= fade_out

        # 3. 輸出檔案
        filename = f"Quick_{ms}ms_Vol{int(intensity_val)}.wav"
        save_wav(filename, audio)

    except ValueError:
        print("❌ 輸入錯誤，請確認輸入的是數字。")


# ===========================
#      主程式
# ===========================
if __name__ == "__main__":
    while True:
        print("\n==============================")
        print(" 手錶震動產生器 v6.1 ")
        print("==============================")
        print("1. 正常震動 (分開輸入長度、強度)")
        print("2. 多段自訂 (設定每段長度與音量)")
        print("3. 讀取 WAV 檔 (分析)")
        print("4. 快速生成 (一行指令：長度 強度)")
        print("q. 離開程式")

        choice = input("請選擇模式 (1/2/3/4/q): ").lower()

        if choice == '1':
            mode_normal()
        elif choice == '2':
            mode_advanced_segments()
        elif choice == '3':
            mode_analyze_sequence()
        elif choice == '4':
            mode_quick_generate()
        elif choice == 'q':
            print("Bye Bye! 👋")
            break
        else:
            print("無效選擇，請重試")