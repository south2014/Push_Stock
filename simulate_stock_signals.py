"""模拟股票信号写入器 - 每5秒向文件写入一条股票信号.

用于测试Push_Stock系统的文件监控功能.

使用方法:
    python simulate_stock_signals.py

按Ctrl+C停止.
"""

import time
import random
from datetime import datetime


def generate_stock_signal():
    """生成随机的股票信号数据.
    
    Returns:
        格式化的股票信号字符串
    """
    # 股票池
    stocks = [
        ("600519", "贵州茅台"),
        ("000858", "五粮液"),
        ("000568", "泸州老窖"),
        ("002304", "洋河股份"),
        ("600809", "山西汾酒"),
        ("000596", "古井贡酒"),
        ("600702", "舍得酒业"),
        ("603198", "迎驾贡酒"),
        ("603369", "今世缘"),
        ("600779", "水井坊"),
    ]
    
    # 随机选择一只股票
    code, name = random.choice(stocks)
    
    # 生成随机价格 (50-2000)
    price = round(random.uniform(50, 2000), 2)
    
    # 生成随机涨跌幅 (-5% 到 +5%)
    change = round(random.uniform(-5, 5), 2)
    change_str = f"{change:+.2f}%"
    
    # 生成随机成交量 (0-5000手)
    volume = random.randint(0, 5000)
    
    # 指标标识
    indicators = ["BBIHTM_G", "MACD_G", "KDJ_G", "RSI_G", "BOLL_G"]
    indicator = random.choice(indicators)
    
    # 当前时间
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M")
    
    # 格式化输出 (使用制表符分隔)
    signal = f"{code}\t{name}\t{time_str}\t{price:.2f}\t{change_str:>7}\t{volume:>6}\t{indicator}"
    
    return signal


def main():
    """主函数."""
    # 目标文件
    target_file = r"F:\OpenCode\Push_Stock\回调买.txt"
    
    print("=" * 60)
    print("股票信号模拟器")
    print("=" * 60)
    print(f"目标文件: {target_file}")
    print(f"写入间隔: 5秒")
    print("按 Ctrl+C 停止")
    print("=" * 60)
    print()
    
    count = 0
    
    try:
        while True:
            # 生成股票信号
            signal = generate_stock_signal()
            
            # 追加写入文件
            with open(target_file, "a", encoding="utf-8") as f:
                f.write(signal + "\n")
            
            count += 1
            now = datetime.now().strftime("%H:%M:%S")
            print(f"[{now}] 第{count:03d}条: {signal}")
            
            # 等待5秒
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\n")
        print("=" * 60)
        print(f"已停止. 共写入 {count} 条股票信号")
        print("=" * 60)


if __name__ == "__main__":
    main()
