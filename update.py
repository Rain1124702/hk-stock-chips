#!/usr/bin/env python3
"""港股籌碼每日更新 - 完整版（含入場/止損/目標/好壞判斷/搜尋）"""
import json
import datetime
from pathlib import Path
from collections import Counter

try:
    import yfinance as yf
    import pandas as pd
    import numpy as np
except ImportError:
    raise SystemExit("pip install yfinance pandas numpy")

NAME_MAP = {
    "0700.HK": "騰訊控股", "9988.HK": "阿里巴巴-SW", "3690.HK": "美團-W",
    "1810.HK": "小米集團-W", "9618.HK": "京東集團-SW", "1024.HK": "快手-W",
    "9999.HK": "網易-S", "9888.HK": "百度集團-SW", "9626.HK": "嗶哩嗶哩-W",
    "2015.HK": "理想汽車-W", "9868.HK": "小鵬汽車-W", "6618.HK": "京東健康",
    "0939.HK": "建設銀行", "1398.HK": "工商銀行", "3988.HK": "中國銀行",
    "2318.HK": "中國平安", "2388.HK": "中銀香港", "0005.HK": "匯豐控股",
    "1299.HK": "友邦保險", "2628.HK": "中國人壽", "3968.HK": "招商銀行",
    "6886.HK": "華泰證券", "0001.HK": "長和", "0002.HK": "中電控股",
    "0003.HK": "中華煤氣", "0006.HK": "電能實業", "0016.HK": "新鴻基地產",
    "0017.HK": "新世界發展", "0066.HK": "港鐵公司", "0267.HK": "中信股份",
    "0688.HK": "中國海外發展", "0823.HK": "領展房產基金", "1109.HK": "華潤置地",
    "1997.HK": "九龍倉置業", "1211.HK": "比亞迪股份", "9866.HK": "蔚來-SW",
    "9863.HK": "零跑汽車", "0981.HK": "中芯國際", "1347.HK": "華虹半導體",
    "1888.HK": "建滔積層板", "2269.HK": "藥明生物", "1093.HK": "石藥集團",
    "1177.HK": "中國生物製藥", "1801.HK": "信達生物", "6160.HK": "百濟神州",
    "1919.HK": "中遠海控", "0386.HK": "中國石油化工股份", "0857.HK": "中國石油股份",
    "0883.HK": "中國海洋石油", "1088.HK": "中國神華", "1171.HK": "兗礦能源",
    "2020.HK": "安踏體育", "2313.HK": "申洲國際", "2382.HK": "舜宇光學科技",
    "2688.HK": "新奧能源", "2883.HK": "中海油田服務", "3328.HK": "交通銀行",
    "6098.HK": "碧桂園服務", "6862.HK": "海底撈",
    "0175.HK": "吉利汽車", "1928.HK": "金沙中國",
    "2331.HK": "李寧", "2319.HK": "蒙牛乳業", "1044.HK": "恆安國際",
    "0669.HK": "創科實業", "0762.HK": "中國聯通", "0728.HK": "中國電信",
    "0941.HK": "中國移動", "9992.HK": "泡泡瑪特", "0914.HK": "海螺水泥",
    "1800.HK": "中國交通建設", "0027.HK": "銀河娛樂", "1929.HK": "周大福",
    "0135.HK": "崑崙能源", "0968.HK": "信義光能", "2057.HK": "中通快递",
}
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
STOCK_POOL = list(NAME_MAP.keys())

def atr(df, period=14):
    high, low, close = df["High"], df["Low"], df["Close"]
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])

def analyze(ticker):
    try:
        df = yf.Ticker(ticker).history(period="3mo", auto_adjust=True)
    except Exception:
        return None
    if df is None or len(df) < 25:
        return None
    close, volume, high, low = df["Close"], df["Volume"], df["High"], df["Low"]
    amount = close * volume
    last = float(close.iloc[-1])
    prev = float(close.iloc[-2])
    change = (last - prev) / prev * 100 if prev else 0
    last_amt = float(amount.iloc[-1])
    avg5 = float(amount.iloc[-6:-1].mean()) if len(amount) >= 6 else last_amt
    avg20 = float(amount.iloc[-21:-1].mean()) if len(amount) >= 21 else avg5
    vol_ratio = last_amt / avg5 if avg5 > 0 else 1.0
    vol5_ratio = avg5 / avg20 if avg20 > 0 else 1.0
    up_days = 0
    for i in range(1, min(8, len(close))):
        if close.iloc[-i] > close.iloc[-i - 1]:
            up_days += 1
        else:
            break
    ma5 = float(close.iloc[-5:].mean())
    ma10 = float(close.iloc[-10:].mean())
    ma20 = float(close.iloc[-20:].mean())
    high20 = float(high.iloc[-20:].max())
    low20 = float(low.iloc[-20:].min())
    low5 = float(low.iloc[-5:].min())
    try:
        atr14 = atr(df)
    except Exception:
        atr14 = (high20 - low20) / 4
    price_pos = (last - low20) / (high20 - low20 + 1e-9)
    turnover_proxy = float(volume.iloc[-1]) / (float(volume.iloc[-21:-1].mean()) + 1e-9) if len(volume) >= 21 else 1.0
    score = 0.0
    score += min(30, max(0, (vol_ratio - 0.8) * 25))
    score += min(20, max(0, (vol5_ratio - 0.7) * 20))
    score += min(15, up_days * 3)
    score += min(20, max(0, (turnover_proxy - 0.8) * 15))
    score += price_pos * 15
    if last < 0.5 or last_amt < 3_000_000:
        return None
    support = max(ma10, ma20 * 0.98, low5 * 0.99)
    if last > ma5 and vol_ratio > 1.3 and up_days >= 1:
        entry_low, entry_high = round(last * 0.985, 3), round(last * 1.005, 3)
        entry_type = "強勢追價 / 小回"
    elif last > ma20 and price_pos > 0.5:
        entry_low = round(max(support, last * 0.97), 3)
        entry_high = round(last * 0.995, 3)
        entry_type = "回踩支撐"
    else:
        entry_low, entry_high = round(support * 0.99, 3), round(support * 1.01, 3)
        entry_type = "等回調至支撐"
    stop = round(entry_low - 1.3 * atr14, 3)
    stop = max(stop, low20 * 0.97)
    if stop >= entry_low:
        stop = round(entry_low * 0.96, 3)
    risk = max(entry_low - stop, last * 0.01)
    target1 = min(round(entry_high + risk * 1.5, 3), high20 * 1.08)
    target2 = min(round(entry_high + risk * 2.2, 3), high20 * 1.15)
    reasons = []
    if vol_ratio >= 1.8:
        reasons.append(f"今日成交額為5日均量的{vol_ratio:.1f}倍，量能明顯放大")
    elif vol_ratio >= 1.3:
        reasons.append(f"今日成交額為5日均量的{vol_ratio:.1f}倍，資金關注度上升")
    if up_days >= 2:
        reasons.append(f"已連續{up_days}日收漲，短期動能延續")
    if last > ma20:
        reasons.append(f"站上20日線({ma20:.2f})，中期趨勢偏多")
    else:
        reasons.append(f"現價仍低於20日線({ma20:.2f})，宜等站穩再考慮")
    if price_pos > 0.7:
        reasons.append("價格處於近20日偏高位置，追高需控制倉位")
    elif price_pos < 0.35:
        reasons.append("價格處於近20日偏低區間，具備反彈空間")
    if turnover_proxy > 1.5:
        reasons.append("換手明顯活躍，短線波動可能加大")
    reason_text = "；".join(reasons) if reasons else "量能與動能中性"
    score_f, change_f = round(score, 1), round(change, 2)
    if score_f >= 40 and change_f > 0 and vol_ratio >= 1.3:
        level, color = "偏多（較值得關注）", "good"
        advice = "量能與動能同時轉強，短線可考慮在建議入場區間分批進場，嚴格守止損。"
    elif score_f >= 28 and change_f >= 0:
        level, color = "中性偏多", "neutral"
        advice = "有一定資金關注，但未達強勢，適合等回踩支撐再考慮，不宜追高。"
    elif score_f >= 20:
        level, color = "中性", "neutral"
        advice = "訊號不明顯，建議觀望或只小倉位試探。"
    else:
        level, color = "偏弱（暫不宜追）", "bad"
        advice = "量能或動能不足，目前較不適合新開倉。"
    detail = (
        f"【綜合判斷】{level}\n\n【現況摘要】\n"
        f"收盤 {round(last, 3)}，當日漲跌 {change_f:+.2f}%，評分 {score_f}。\n"
        f"入場類型：{entry_type}。\n\n【量能與動能】\n{reason_text}\n\n"
        f"【操作建議】\n{advice}\n\n【風險提示】\n"
        f"止損設於 {stop}。目標 1 約 {target1}、目標 2 約 {target2}。\n"
        f"本分析僅基於公開價量，僅供研究參考。"
    )
    return {
        "code": ticker.replace(".HK", ""),
        "name": NAME_MAP.get(ticker, ticker),
        "sector": SECTOR_MAP.get(ticker, "其他"),
        "close": round(last, 3),
        "change": change_f,
        "volume": int(volume.iloc[-1]),
        "amount": last_amt,
        "amount_yi": round(last_amt / 1e8, 3),
        "turnover": round(min(turnover_proxy / 20, 0.5), 4),
        "score": score_f,
        "up_days": up_days,
        "vol_ratio": round(vol_ratio, 2),
        "ma20": round(ma20, 3),
        "entry_low": entry_low,
        "entry_high": entry_high,
        "entry_type": entry_type,
        "stop": stop,
        "target1": target1,
        "target2": target2,
        "reason": reason_text,
        "atr": round(atr14, 3),
        "verdict": level,
        "verdict_color": color,
        "detail_text": detail,
    }

def main():
    print("開始抓取港股數據...")
    results = []
    for i, t in enumerate(STOCK_POOL):
        print(f"  [{i+1}/{len(STOCK_POOL)}] {t}", end="\r")
        r = analyze(t)
        if r:
            results.append(r)
    print(f"\n有效股票：{len(results)} 檔")
    if not results:
        print("沒有有效數據，結束")
        return
    picks = sorted(results, key=lambda x: x["score"], reverse=True)[:30]
    volume_top = sorted(results, key=lambda x: x["amount"], reverse=True)[:20]
    turnover_top = sorted(results, key=lambda x: x["turnover"], reverse=True)[:20]
    up = sum(1 for p in picks if p["change"] > 0)
    down = len(picks) - up
    avg_score = sum(p["score"] for p in picks) / len(picks)
    top_sector = Counter(p["sector"] for p in picks).most_common(1)[0][0]
    by_code = {x["code"]: x for x in results}
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
        "all_stocks": list(by_code.values()),
    }
    out = Path(__file__).resolve().parent / "data.js"
    out.write_text("const DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print(f"已寫入 {out}")
    for i, p in enumerate(picks[:5], 1):
        print(f"  {i}. {p['name']} 收{p['close']} 分數{p['score']} 入場{p['entry_low']}-{p['entry_high']}")

if __name__ == "__main__":
    main()
