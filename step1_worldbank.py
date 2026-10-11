"""
===============================================================
 Step 1: 从 World Bank 获取真实宏观数据
 不需要API key，完全免费
===============================================================
"""

import pandas as pd
import numpy as np
import requests
import time


def fetch_world_bank_data():
    """获取各国 World Bank 宏观指标"""
    indicators = {
        'IT.NET.USER.ZS': 'Internet_Penetration_Real',   # 互联网普及率
        'NY.GDP.PCAP.CD': 'GDP_per_Capita',               # 人均GDP
        'SP.POP.TOTL': 'Population',                       # 总人口
        'SP.URB.TOTL.IN.ZS': 'Urbanization_Rate',         # 城市化率
        'IT.CEL.SETS.P2': 'Mobile_Subscriptions'           # 移动手机订阅
    }

    countries = {
        'AR': 'Argentina', 'AU': 'Australia', 'BR': 'Brazil',
        'CA': 'Canada', 'CN': 'China', 'FR': 'France',
        'DE': 'Germany', 'IN': 'India', 'ID': 'Indonesia',
        'IT': 'Italy', 'JP': 'Japan', 'MX': 'Mexico',
        'NL': 'Netherlands', 'PL': 'Poland', 'RU': 'Russia',
        'SG': 'Singapore', 'ES': 'Spain', 'SE': 'Sweden',
        'TH': 'Thailand', 'TR': 'Turkey',
        # 额外补充国家（为后续扩充准备）
        'KR': 'South Korea', 'GB': 'United Kingdom',
        'US': 'United States', 'ZA': 'South Africa',
        'SA': 'Saudi Arabia', 'VN': 'Vietnam',
        'PH': 'Philippines', 'MY': 'Malaysia',
        'DK': 'Denmark', 'NO': 'Norway',
        'FI': 'Finland', 'CH': 'Switzerland',
        'BE': 'Belgium', 'PT': 'Portugal', 'CL': 'Chile'
    }

    results = {name: {} for name in countries.values()}

    for code, name in countries.items():
        results[name]['ISO'] = code

    for ind_code, ind_name in indicators.items():
        print(f"  获取: {ind_name} ...", end=' ')
        success = 0
        for iso_code, country_name in countries.items():
            url = (f"https://api.worldbank.org/v2/country/{iso_code}/"
                   f"indicator/{ind_code}?format=json&date=2020:2024&per_page=10")
            try:
                resp = requests.get(url, timeout=15)
                data = resp.json()
                if isinstance(data, list) and len(data) > 1 and data[1]:
                    vals = [item['value'] for item in data[1]
                            if item['value'] is not None]
                    if vals:
                        # 取2022-2024最新均值（最多3年）
                        results[country_name][ind_name] = np.mean(vals[:3])
                        success += 1
                    else:
                        results[country_name][ind_name] = np.nan
                else:
                    results[country_name][ind_name] = np.nan
            except Exception:
                results[country_name][ind_name] = np.nan
            time.sleep(0.25)
        print(f"成功获取 {success}/{len(countries)} 个国家")

    df = pd.DataFrame.from_dict(results, orient='index').reset_index()
    df = df.rename(columns={'index': 'Country'})
    return df


if __name__ == '__main__':
    print("=" * 60)
    print("  World Bank 真实宏观数据采集")
    print("=" * 60)
    df = fetch_world_bank_data()
    df.to_csv('world_bank_real.csv', index=False, encoding='utf-8-sig')
    print(f"\n✅ 已保存至 world_bank_real.csv")
    print(f"   覆盖 {len(df)} 个国家")
    print(f"   列: {list(df.columns)}")
