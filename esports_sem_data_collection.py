"""
===============================================================
 电竞跨文化传播SEM研究 —— 数据采集脚本 v1.0
===============================================================
采集目标：
  1. Hofstede 文化维度数据
  2. 全球电竞行业数据 (Kaggle + Liquipedia)
  3. World Bank 宏观控制变量

作者注：本脚本将所有源合并为一个 master DataFrame，
        以国家为分析单位，可直接导入 SmartPLS / AMOS / lavaan。
===============================================================
"""

import pandas as pd
import numpy as np
import requests
import time
import warnings
warnings.filterwarnings('ignore')

# =============================================================
# 第一部分：Hofstede 文化维度数据
# =============================================================
# 方式 A：从Kaggle下载后读取本地CSV
# 下载地址: https://www.kaggle.com/datasets/seydakaba/hofstede-cultural-dimensions-by-country
# 将下载的 CSV 放在本脚本同目录下，命名为 hofstede.csv
#
# 方式 B：如果不想下载，下面嵌入了一份常用国家数据

def load_hofstede_data(filepath='hofstede.csv'):
    """
    读取 Hofstede 文化维度 CSV
    如果文件不存在，使用内置的备用数据
    """
    try:
        df = pd.read_csv(filepath)
        print(f"[OK] Hofstede数据已加载: {len(df)} 个国家")
        return df
    except FileNotFoundError:
        print("[!] 未找到 hofstede.csv，使用内置备用数据（35个常用国家）")
        return _get_fallback_hofstede()


def _get_fallback_hofstede():
    """
    内置备用数据：35个主要电竞国家的Hofstede六维度得分
    来源：geerthofstede.com
    """
    data = {
        'Country': [
            'South Korea', 'China', 'Japan', 'United States', 'Brazil',
            'Germany', 'United Kingdom', 'France', 'Russia', 'India',
            'Canada', 'Australia', 'Sweden', 'Poland', 'Vietnam',
            'Philippines', 'Indonesia', 'Malaysia', 'Thailand', 'Singapore',
            'Turkey', 'Mexico', 'Argentina', 'Chile', 'Saudi Arabia',
            'Spain', 'Italy', 'Netherlands', 'Denmark', 'Norway',
            'Finland', 'Switzerland', 'Belgium', 'Portugal', 'South Africa'
        ],
        'Power_Distance': [
            60, 80, 54, 40, 69, 35, 35, 68, 93, 77,
            39, 36, 31, 68, 70, 94, 78, 100, 64, 74,
            66, 81, 49, 63, 95, 57, 50, 38, 18, 31,
            33, 34, 65, 63, 49
        ],
        'Individualism': [
            18, 20, 46, 91, 38, 67, 89, 71, 39, 48,
            80, 90, 71, 60, 20, 32, 14, 26, 20, 20,
            37, 30, 46, 23, 25, 51, 76, 80, 74, 69,
            63, 68, 75, 27, 65
        ],
        'Masculinity': [
            39, 66, 95, 62, 49, 66, 66, 43, 36, 56,
            52, 61, 5, 64, 40, 64, 46, 50, 34, 48,
            45, 69, 56, 28, 60, 42, 70, 14, 16, 8,
            26, 70, 54, 31, 63
        ],
        'Uncertainty_Avoidance': [
            85, 30, 92, 46, 76, 65, 35, 86, 95, 40,
            48, 51, 29, 93, 30, 44, 48, 36, 64, 8,
            85, 82, 86, 86, 80, 86, 75, 53, 23, 50,
            59, 58, 94, 104, 49
        ],
        'Long_Term_Orientation': [
            100, 87, 88, 26, 44, 83, 51, 63, 81, 51,
            36, 21, 53, 38, 57, 27, 62, 41, 32, 72,
            46, 24, 20, 31, 36, 48, 61, 67, 35, 35,
            38, 74, 82, 28, 34
        ],
        'Indulgence': [
            29, 24, 42, 68, 59, 40, 69, 48, 20, 26,
            68, 71, 78, 29, 35, 42, 38, 57, 45, 46,
            49, 97, 62, 68, 52, 44, 30, 68, 70, 55,
            57, 66, 57, 33, 63
        ]
    }
    return pd.DataFrame(data)


# =============================================================
# 第二部分：Kaggle 电竞数据
# =============================================================
# Kaggle数据集下载：
# https://www.kaggle.com/datasets/emirhanakku/global-gaming-and-esports-growth-dataset-20102025
#
# 下载后解压，将 CSV 放在本脚本同目录下，命名为 gaming_esports.csv
#
# 这个数据集是合成数据（synthetic），但变量结构设计合理。
# 在正式论文中，应该用它做模型开发，用真实API数据（Liquipedia等）做验证。

def load_kaggle_esports(filepath='gaming_esports.csv'):
    """
    读取Kaggle电竞数据集
    仅保留最近年份（2023-2025）的数据作为当前截面
    """
    try:
        df = pd.read_csv(filepath)
        print(f"[OK] Kaggle电竞数据已加载: {len(df)} 条记录")

        # 保留最近年份（取2023-2025均值，减少单年波动）
        df_recent = df[df['Year'] >= 2023].copy()

        # 按国家聚合为截面数据
        df_agg = df_recent.groupby('Country').agg({
            'Esports_Revenue_MillionUSD': 'mean',
            'Esports_Viewers_Million': 'mean',
            'Active_Players_Million': 'mean',
            'Esports_Tournaments_Count': 'mean',
            'Pro_Players_Count': 'mean',
            'Esports_PrizePool_MillionUSD': 'mean',
            'Streaming_Influence_Index': 'mean',
            'Internet_Penetration_Percent': 'mean',
            'Mobile_Gaming_Share': 'mean',
            'Female_Gamer_Percent': 'mean',
            'Gaming_Companies_Count': 'mean',
            'Avg_Playtime_HoursPerWeek': 'mean',
            'Avg_Spending_USD': 'mean',
            'AR_VR_Adoption_Index': 'mean'
        }).reset_index()

        print(f"[OK] 聚合为截面数据: {len(df_agg)} 个国家 (2023-2025均值)")
        return df_agg
    except FileNotFoundError:
        print("[!] 未找到 gaming_esports.csv")
        print("    下载地址: https://www.kaggle.com/datasets/emirhanakku/"
              "global-gaming-and-esports-growth-dataset-20102025")
        print("    将文件放到脚本同目录后重新运行")
        return None


# =============================================================
# 第三部分：Liquipedia API 数据
# =============================================================
# Liquipedia API 需要申请教育访问权限:
#   https://liquipedia.net/api
# 申请时说明: "Academic research on esports cross-cultural communication"
#
# 批准后你会获得 API key。下面脚本是获取数据后如何聚合为SEM变量的框架。

def fetch_from_liquipedia(api_key=None):
    """
    从Liquipedia API获取各国电竞数据

    注意：需要提前申请API key。
    如果你还没有API key，这个函数会返回None，
    你可以先用Kaggle数据替代。

    申请获得API key后，将 key 填入下方代码即可运行。
    """
    if not api_key:
        print("[!] 未提供Liquipedia API key，跳过Liquipedia数据采集")
        print("    申请地址: https://liquipedia.net/api")
        return None

    # --- 以下为API使用示例 ---
    # Liquipedia LPDB API 端点示例
    # 具体端点路径请参照申请后收到的API文档

    headers = {'Authorization': f'Bearer {api_key}'}

    # 示例：获取各国家战队数据
    # 实际端点以官方文档为准
    # url = 'https://api.liquipedia.net/v1/teams'
    # params = {'game': 'league-of-legends', 'limit': 1000}
    # response = requests.get(url, headers=headers, params=params)

    print("[*] Liquipedia API key 已配置，可开始数据采集")
    print("    具体API端点请参照官方文档")
    return None


# =============================================================
# 第四部分：World Bank 数据
# =============================================================
# 完全免费，不需要API key

def fetch_world_bank_data():
    """
    从 World Bank API 获取各国宏观指标
    使用直接HTTP请求，无需安装额外库
    """
    indicators = {
        'IT.NET.USER.ZS': 'Internet_Penetration',
        'NY.GDP.PCAP.CD': 'GDP_per_Capita',
        'SP.POP.TOTL': 'Population',
        'SP.URB.TOTL.IN.ZS': 'Urbanization',
        'IT.CEL.SETS.P2': 'Mobile_Subscriptions'
    }

    # 主要电竞国家ISO代码
    countries = {
        'KR': 'South Korea', 'CN': 'China', 'JP': 'Japan',
        'US': 'United States', 'BR': 'Brazil', 'DE': 'Germany',
        'GB': 'United Kingdom', 'FR': 'France', 'RU': 'Russia',
        'IN': 'India', 'CA': 'Canada', 'AU': 'Australia',
        'SE': 'Sweden', 'PL': 'Poland', 'VN': 'Vietnam',
        'PH': 'Philippines', 'ID': 'Indonesia', 'MY': 'Malaysia',
        'TH': 'Thailand', 'SG': 'Singapore', 'TR': 'Turkey',
        'MX': 'Mexico', 'AR': 'Argentina', 'CL': 'Chile',
        'SA': 'Saudi Arabia', 'ES': 'Spain', 'IT': 'Italy',
        'NL': 'Netherlands', 'DK': 'Denmark', 'NO': 'Norway',
        'FI': 'Finland', 'CH': 'Switzerland', 'BE': 'Belgium',
        'PT': 'Portugal', 'ZA': 'South Africa'
    }

    results = {}

    for iso_code, country_name in countries.items():
        results[country_name] = {'ISO': iso_code}

    for indicator_code, indicator_name in indicators.items():
        print(f"  正在获取: {indicator_name} ...")

        for iso_code in countries.keys():
            url = (
                f"https://api.worldbank.org/v2/country/{iso_code}/"
                f"indicator/{indicator_code}?format=json&date=2020:2024"
                f"&per_page=10"
            )

            try:
                resp = requests.get(url, timeout=15)
                data = resp.json()

                if isinstance(data, list) and len(data) > 1 and data[1]:
                    # 取2022-2024年最新非空值的均值
                    values = [
                        item['value'] for item in data[1]
                        if item['value'] is not None
                    ]
                    if values:
                        results[countries[iso_code]][indicator_name] = np.mean(values)
                    else:
                        results[countries[iso_code]][indicator_name] = np.nan
                else:
                    results[countries[iso_code]][indicator_name] = np.nan
            except Exception as e:
                results[countries[iso_code]][indicator_name] = np.nan

            # API限流：每请求间隔0.3秒
            time.sleep(0.3)

    df = pd.DataFrame.from_dict(results, orient='index').reset_index()
    df = df.rename(columns={'index': 'Country'})

    valid_count = df['Internet_Penetration'].notna().sum()
    print(f"[OK] World Bank数据采集完成: {valid_count}/{len(countries)} 个国家有完整数据")

    return df


# =============================================================
# 第五部分：计算衍生变量（构建SEM潜变量的测量指标）
# =============================================================

def compute_derived_variables(df):
    """
    根据原始数据计算SEM模型需要的潜变量测量指标

    潜变量设计：

    LV1: 电竞产业国际化程度 (Esports Internationalization)
         - 指标1: 人均奖金池 (PrizePool_per_Capita)
         - 指标2: 人均职业选手 (ProPlayers_per_Million)
         - 指标3: 人均赛事数 (Tournaments_per_Million)
         - 指标4: 电竞收入占GDP比重 (Esports_Revenue_Share)

    LV2: 跨文化传播效能 (Cross-cultural Communication Efficacy)
         - 指标1: 直播影响力指数 (Streaming_Influence_Index)
         - 指标2: 观众/玩家比 (Viewers_to_Players_Ratio)
         - 指标3: 国际电竞参与度 (International_Engagement) *

    LV3: 文化开放性 (Cultural Openness)
         - 指标1: 个人主义得分反向编码 (Individualism)
         - 指标2: 不确定性规避反向编码 (Uncertainty_Avoidance_rev)
         - 指标3: 放纵度 (Indulgence)

    LV4: 技术基础设施 (Tech Infrastructure)
         - 指标1: 互联网普及率 (Internet_Penetration)
         - 指标2: 人均GDP对数 (log_GDP_per_Capita)
         - 指标3: 移动订阅率 (Mobile_Subscriptions)

    * 注：International_Engagement 需要Liquipedia数据计算，
      如没有则用观看量/观众数替代。
    """

    # 确保必要列存在
    required = [
        'Esports_PrizePool_MillionUSD', 'Population',
        'Pro_Players_Count', 'Esports_Tournaments_Count',
        'Esports_Revenue_MillionUSD', 'GDP_per_Capita',
        'Esports_Viewers_Million', 'Active_Players_Million',
        'Streaming_Influence_Index'
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"[!] 缺少必要列: {missing}")
        print("    部分衍生变量将跳过")

    # --- LV1: 电竞产业国际化 ---
    if all(c in df.columns for c in required[:4]):
        df['PrizePool_per_Capita'] = (
            df['Esports_PrizePool_MillionUSD'] * 1e6 / df['Population']
        )
        df['ProPlayers_per_Million'] = (
            df['Pro_Players_Count'] / (df['Population'] / 1e6)
        )
        df['Tournaments_per_Million'] = (
            df['Esports_Tournaments_Count'] / (df['Population'] / 1e6)
        )

    if all(c in df.columns for c in ['Esports_Revenue_MillionUSD', 'GDP_per_Capita', 'Population']):
        df['GDP_Total'] = df['GDP_per_Capita'] * df['Population']
        df['Esports_Revenue_Share'] = (
            df['Esports_Revenue_MillionUSD'] * 1e6 / df['GDP_Total'] * 100
        )

    # --- LV2: 跨文化传播效能 ---
    if all(c in df.columns for c in ['Esports_Viewers_Million', 'Active_Players_Million']):
        df['Viewers_to_Players_Ratio'] = (
            df['Esports_Viewers_Million'] / df['Active_Players_Million'].replace(0, np.nan)
        )

    # --- LV4: 技术基础设施 ---
    if 'GDP_per_Capita' in df.columns:
        df['log_GDP_per_Capita'] = np.log(df['GDP_per_Capita'].replace(0, np.nan))

    # 文化变量已在Hofstede数据中
    if 'Uncertainty_Avoidance' in df.columns:
        # 不确定性规避反向编码（越低的文化开放性越高）
        max_val = df['Uncertainty_Avoidance'].max()
        df['Uncertainty_Avoidance_rev'] = max_val - df['Uncertainty_Avoidance']

    print("[OK] 衍生变量计算完成")
    return df


# =============================================================
# 第六部分：合并所有数据源
# =============================================================

def merge_all_data():
    """
    主函数：合并所有数据源为一个master DataFrame
    """
    print("=" * 60)
    print("  电竞跨文化传播SEM研究 - 数据采集")
    print("=" * 60)

    # Step 1: 加载Hofstede数据
    print("\n[1/4] 加载Hofstede文化维度数据...")
    df_hofstede = load_hofstede_data()

    # Step 2: 加载Kaggle电竞数据
    print("\n[2/4] 加载Kaggle电竞数据...")
    df_esports = load_kaggle_esports()

    if df_esports is None:
        print("[!] 请先下载 Kaggle 数据集")
        print("    下载链接: https://www.kaggle.com/datasets/"
              "emirhanakku/global-gaming-and-esports-growth-dataset-20102025")
        return None

    # Step 3: 获取World Bank数据
    print("\n[3/4] 获取World Bank宏观数据...")
    df_worldbank = fetch_world_bank_data()

    # Step 4: 合并数据集
    print("\n[4/4] 合并数据集...")

    # 先合并电竞数据 + Hofstede
    df_master = pd.merge(df_esports, df_hofstede, on='Country', how='inner')
    print(f"  合并Hofstede后: {len(df_master)} 个国家")

    # 再合并World Bank
    df_master = pd.merge(df_master, df_worldbank, on='Country', how='left')
    print(f"  合并World Bank后: {len(df_master)} 个国家")

    # Step 5: 计算衍生变量
    print("\n  计算SEM潜变量测量指标...")
    df_master = compute_derived_variables(df_master)

    # Step 6: 基本信息
    print(f"\n{'=' * 60}")
    print(f"  最终数据集: {len(df_master)} 个国家 × {len(df_master.columns)} 个变量")
    print(f"{'=' * 60}")

    # 列出可用列
    print("\n可用变量:")
    for col in df_master.columns:
        print(f"  - {col}")

    return df_master


# =============================================================
# 运行
# =============================================================

if __name__ == '__main__':
    df = merge_all_data()

    if df is not None:
        # 保存为CSV
        output_path = 'esports_sem_master_data.csv'
        df.to_csv(output_path, index=False)
        print(f"\n[SAVED] 数据已保存至: {output_path}")
        print("        可直接导入 SmartPLS / AMOS / R lavaan 进行分析")

        # 显示前5行概览
        print("\n数据预览:")
        print(df.head())

        # 描述统计
        print("\n描述统计:")
        desc_cols = [
            c for c in df.columns
            if df[c].dtype in ['float64', 'int64']
        ]
        print(df[desc_cols].describe())
    else:
        print("\n[!] 数据采集未完成，请检查上述错误信息")
