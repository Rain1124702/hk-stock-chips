#!/usr/bin/env python3
"""
港股籌碼推薦系統 - 資料更新腳本
用法：python update.py
需要：pip install yfinance pandas numpy
"""

import json
import datetime
from pathlib import Path

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError:
    print("請先安裝依賴：pip install yfinance pandas numpy")
    raise SystemExit(1)

# 常見港股主板 + 部分創業板熱門股票（可自行擴充）
# 格式：Yahoo 代號（4位數字.HK）
STOCK_POOL = list(dict.fromkeys([
    # 大型權值 / 科技
    "0700.HK", "9988.HK", "3690.HK", "1810.HK", "9618.HK", "1024.HK", "9999.HK",
    "9888.HK", "9626.HK", "2015.HK", "9868.HK", "6618.HK",
    # 金融
    "0939.HK", "1398.HK", "3988.HK", "2318.HK", "2388.HK", "0005.HK", "1299.HK",
    "2628.HK", "3968.HK", "6886.HK",
    # 消費 / 地產 / 其他
    "0001.HK", "0002.HK", "0003.HK", "0006.HK", "0011.HK", "0016.HK", "0017.HK",
    "0066.HK", "0267.HK", "0688.HK", "0823.HK", "1109.HK", "1997.HK",
    # 新能源 / 汽車 / 半導體
    "1211.HK", "9866.HK", "9863.HK", "0981.HK", "1347.HK", "1888.HK",
    # 醫藥 / 生物
    "2269.HK", "1093.HK", "1177.HK", "1801.HK", "6160.HK", "9995.HK",
    # 其他活躍股
    "1919.HK", "0386.HK", "0857.HK", "0883.HK", "1088.HK", "1171.HK",
    "2020.HK", "2313.HK", "2382.HK", "2688.HK", "2883.HK", "3328.HK",
    "6098.HK", "6862.HK",
]))

# 中文名稱對照（避免 yfinance 名稱抓取失敗）
NAME_MAP = {
    "0700.HK": "騰訊控股", "9988.HK": "阿里巴巴-SW", "3690.HK": "美團-W",
    "1810.HK": "小米集團-W", "9618.HK": "京東集團-SW", "1024.HK": "快手-W",
    "9999.HK": "網易-S", "9888.HK": "百度集團-SW", "9626.HK": "嗶哩嗶哩-W",
    "2015.HK": "理想汽車-W", "9868.HK": "小鵬汽車-W", "6618.HK": "京東健康",
    "0939.HK": "建設銀行", "1398.HK": "工商銀行", "3988.HK": "中國銀行",
    "2318.HK": "中國平安", "2388.HK": "中銀香港", "0005.HK": "匯豐控股",
    "1299.HK": "友邦保險", "2628.HK": "中國人壽", "3968.HK": "招商銀行",
    "6886.HK": "華泰證券", "0001.HK": "長和", "0002.HK": "中電控股",
    "0003.HK": "中華煤氣", "0006.HK": "電能實業", "0011.HK": "恆生銀行",
    "0016.HK": "新鴻基地產", "0017.HK": "新世界發展", "0066.HK": "港鐵公司",
    "0267.HK": "中信股份", "0688.HK": "中國海外發展", "0823.HK": "領展房產基金",
    "1109.HK": "華潤置地", "1997.HK": "九龍倉置業", "1211.HK": "比亞迪股份",
    "9866.HK": "蔚來-SW", "9863.HK": "零跑汽車", "0981.HK": "中芯國際",
    "1347.HK": "華虹半導體", "1888.HK": "建滔積層板", "2269.HK": "藥明生物",
    "1093.HK": "石藥集團", "1177.HK": "中國生物製藥", "1801.HK": "信達生物",
    "6160.HK": "百濟神州", "9995.HK": "榮昌生物", "1919.HK": "中遠海控",
    "0386.HK": "中國石油化工股份", "0857.HK": "中國石油股份", "0883.HK": "中國海洋石油",
    "1088.HK": "中國神華", "1171.HK": "兗礦能源", "2020.HK": "安踏體育",
    "2313.HK": "申洲國際", "2382.HK": "舜宇光學科技", "2688.HK": "新奧能源",
    "2883.HK": "中海油田服務", "3328.HK": "交通銀行", "6098.HK": "碧桂園服務",
    "6862.HK": "海底撈",
}

# 簡單產業對照
SECTOR_MAP = {
    "0700.HK": "科技", "9988.HK": "科技", "3690.HK": "科技", "1810.HK": "消費電子",
    "9618.HK": "電商", "1024.HK": "科技", "9999.HK": "科技", "9888.HK": "科技",
    "9626.HK": "科技", "2015.HK": "汽車", "9868.HK": "汽車", "6618.HK": "醫療",
    "0939.HK": "金融", "1398.HK": "金融", "3988.HK": "金融", "2318.HK": "保險",
    "2388.HK": "金融", "0005.HK": "金融", "1299.HK": "保險", "2628.HK": "保險",
    "3968.HK": "金融", "6886.HK": "金融", "0001.HK": "綜合", "0002.HK": "公用",
    "0003.HK": "公用", "0016.HK": "地產", "1211.HK": "汽車", "0981.HK": "半導體",
    "2269.HK": "醫藥", "1919.HK": "航運", "0386.HK": "能源", "0857.HK": "能源",
    "0883.HK": "能源", "1088.HK": "能源", "9863.HK": "汽車", "9866.HK": "汽車",
}


def fetch_history(ticker: str, period: str = "2mo") -> pd.DataFrame:
    try:
        t = yf.Ticker(ticker)
        df = t.history(period=period, auto_adjust=True)
        if df.empty or len(df) < 10:
            return pd.DataFrame()
        return df
    except Exception:
        return pd.DataFrame()


def calc_metrics(df: pd.DataFrame) -> dict | None:
    if df.empty or len(df) < 10:
        return None

    close = df["Close"]
    volume = df["Volume"]
    # 成交金額近似（港元）
    amount = close * volume

    last_close = float(close.iloc[-1])
    prev_close = float(close.iloc[-2]) if len(close) > 1 else last_close
    change_pct = (last_close - prev_close) / prev_close * 100 if prev_close else 0

    last_vol = float(volume.iloc[-1])
    last_amount = float(amount.iloc[-1])
    avg5_amount = float(amount.iloc[-6:-1].mean()) if len(amount) >= 6 else last_amount
    avg20_amount = float(amount.iloc[-21:-1].mean()) if len(amount) >= 21 else avg5_amount

    # 連續上漲天數
    up_days = 0
    for i in range(1, min(10, len(close))):
        if close.iloc[-i] > close.iloc[-i - 1]:
            up_days += 1
        else:
            break

    # 相對量能
    vol_ratio = last_amount / avg5_amount if avg5_amount > 0 else 1.0
    vol5_ratio = avg5_amount / avg20_amount if avg20_amount > 0 else 1.0

    # 週轉率近似：用成交量 / 近期平均成交量作為代理（真實週轉率需股本）
    # 這裡用「相對活躍度」代替
    turnover_proxy = last_vol / (volume.iloc[-21:-1].mean() + 1e-9) if len(volume) >= 21 else 1.0

    # 價格位置（0~1）
    high20 = float(close.iloc[-20:].max())
    low20 = float(close.iloc[-20:].min())
    price_pos = (last_close - low20) / (high20 - low20 + 1e-9)

    # 評分（0~100）
    score = 0.0
    # 1. 當日量能爆發 (30)
    score += min(30, max(0, (vol_ratio - 0.8) * 25))
    # 2. 5日相對量能 (20)
    score += min(20, max(0, (vol5_ratio - 0.7) * 20))
    # 3. 連續強勢天數 (15)
    score += min(15, up_days * 3)
    # 4. 週轉/活躍度 (20)
    score += min(20, max(0, (turnover_proxy - 0.8) * 15))
    # 5. 價格位置 (15)
    score += price_pos * 15

    return {
        "close": round(last_close, 3),
        "change": round(change_pct, 2),
        "volume": int(last_vol),
        "amount": last_amount,
        "amount_yi": round(last_amount / 1e8, 3),  # 億港元
        "turnover": round(min(turnover_proxy / 20, 0.5), 4),  # 近似值
        "score": round(score, 1),
        "up_days": up_days,
        "vol_ratio": round(vol_ratio, 2),
    }


def main():
    print("開始抓取港股資料（約需 1–3 分鐘）...")
    results = []

    for i, ticker in enumerate(STOCK_POOL):
        print(f"  [{i+1}/{len(STOCK_POOL)}] {ticker}", end="\r")
        df = fetch_history(ticker)
        m = calc_metrics(df)
        if not m:
            continue
        # 篩選條件
        if m["close"] < 0.5 or m["amount"] < 3_000_000:
            continue
        code = ticker.replace(".HK", "")
        name = NAME_MAP.get(ticker, ticker)
        results.append({
            "code": code,
            "name": name,
            "sector": SECTOR_MAP.get(ticker, "其他"),
            **m
        })

    print(f"\n有效股票：{len(results)} 檔")

    if not results:
        print("沒有抓到有效資料，請檢查網路或稍後再試。")
        return

    # 排序
    picks = sorted(results, key=lambda x: x["score"], reverse=True)[:30]
    volume_top = sorted(results, key=lambda x: x["amount"], reverse=True)[:20]
    turnover_top = sorted(results, key=lambda x: x["turnover"], reverse=True)[:20]

    up = sum(1 for p in picks if p["change"] > 0)
    down = len(picks) - up
    avg_score = sum(p["score"] for p in picks) / len(picks) if picks else 0
    from collections import Counter
    sector_cnt = Counter(p["sector"] for p in picks)
    top_sector = sector_cnt.most_common(1)[0][0] if sector_cnt else "—"

    data = {
        "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": {
            "rec_count": len(picks),
            "avg_score": round(avg_score, 1),
            "up": up,
            "down": down,
            "top_sector": top_sector,
        },
        "picks": picks,
        "volume_top": volume_top,
        "turnover_top": turnover_top,
    }

    out_path = Path(__file__).parent / "data.js"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("const DATA = ")
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"已寫入 {out_path}")
    print(f"推薦前 5 名：")
    for i, p in enumerate(picks[:5], 1):
        print(f"  {i}. {p['name']} ({p['code']}) 分數 {p['score']} 漲跌 {p['change']}%")


if __name__ == "__main__":
    main()
