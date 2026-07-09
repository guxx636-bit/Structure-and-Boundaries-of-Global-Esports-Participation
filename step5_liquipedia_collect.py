"""
===============================================================
 Step 5: LiquipediaDB API v3 — 完整数据采集脚本
===============================================================
 采集20个国家 × 4款游戏的:
  - 选手数（按国籍统计）
  - 赛事数（按举办国统计）
  - 奖金池（按举办国统计）

 替换 Kaggle 合成数据中的赛事/选手/奖金变量
===============================================================
"""

import requests
import json
import time
import pandas as pd
import numpy as np
import os

API_KEY = "NjpSzj9UGbkMj92mIfZvpMK1SMP9Xbiem7108B1Jnc7X6u0x5BuuTklEna3M5XAn0Dl2Z3ufvY6fTIZQ3EW18HJcNiZXkyVAplAnINrV2Mxae6Gg7IYua9rnkbdPqfFG"
BASE_URL = "https://api.liquipedia.net/api"
HEADERS = {
    "Authorization": f"Apikey {API_KEY}",
    "Accept-Encoding": "gzip",
    "User-Agent": "EsportsSEMResearch/1.0 (academic; hku)"
}

# 20个国家：英文名 → ISO 2字母代码（用于locations匹配）
COUNTRIES = {
    'Argentina': 'ar', 'Australia': 'au', 'Brazil': 'br',
    'Canada': 'ca', 'China': 'cn', 'France': 'fr',
    'Germany': 'de', 'India': 'in', 'Indonesia': 'id',
    'Italy': 'it', 'Japan': 'jp', 'Mexico': 'mx',
    'Netherlands': 'nl', 'Poland': 'pl', 'Russia': 'ru',
    'Singapore': 'sg', 'Spain': 'es', 'Sweden': 'se',
    'Thailand': 'th', 'Turkey': 'tr'
}

# 4款游戏
GAMES = ['leagueoflegends', 'valorant', 'dota2', 'counterstrike']

# 速率控制
DELAY = 0.8  # 请求间隔（秒）


def api_get(endpoint, params):
    """发送API GET请求"""
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        else:
            # 不打印404（正常情况：某国没有该游戏的选手）
            if resp.status_code != 404:
                print(f"  HTTP {resp.status_code}")
            return None
    except Exception as e:
        print(f"  ❌ {e}")
        return None


# =============================================================
# Phase 1: 采集选手数据
# =============================================================
def collect_players():
    """
    按国籍统计各国选手数
    endpoint: /v3/player, filter: nationality
    """
    print("=" * 60)
    print("  Phase 1: 采集选手数据")
    print("=" * 60)

    results = {}
    for country_en, country_iso in COUNTRIES.items():
        results[country_en] = 0

    for game in GAMES:
        print(f"\n  {game}:")
        for country_en, _ in COUNTRIES.items():
            params = {
                'wiki': game,
                'conditions': f'[[nationality::{country_en}]]',
                'limit': 1000
            }
            data = api_get('/v3/player', params)
            count = 0
            if data and 'result' in data:
                count = len(data['result'])
                results[country_en] += count

            if count > 0:
                print(f"    {country_en}: {count}")

            time.sleep(DELAY)

        # 保存中间结果
        df = pd.DataFrame([{'Country': k, 'Player_Count_Real': v} for k, v in results.items()])
        df.to_csv('players_raw.csv', index=False, encoding='utf-8-sig')

    print(f"\n  选手数据采集完成")
    print(f"  中国: {results['China']} 巴西: {results['Brazil']} 俄罗斯: {results['Russia']}")
    print(f"  美国: n/a(不在目标列表)")
    return results


# =============================================================
# Phase 2: 采集赛事数据（按举办国 + 奖金池）
# =============================================================
def collect_tournaments():
    """
    采集2022-2026年S-Tier和A-Tier赛事的举办国和奖金池
    通过 locations 字段的 country1/country2/... 解析
    """
    print("\n" + "=" * 60)
    print("  Phase 2: 采集赛事与奖金数据")
    print("=" * 60)

    tournament_results = {}
    prizepool_results = {}
    for country_en, _ in COUNTRIES.items():
        tournament_results[country_en] = 0
        prizepool_results[country_en] = 0.0

    for game in GAMES:
        print(f"\n  {game}:")
        page = 0
        total_processed = 0

        while True:
            # 每次获取一页（最多1000条）
            params = {
                'wiki': game,
                'conditions': '[[startdate::>2022-01-01]] AND ([[liquipediatier::1]] OR [[liquipediatier::2]])',
                'limit': 1000,
                'offset': page * 1000,
                'order': 'startdate DESC'
            }
            data = api_get('/v3/tournament', params)
            if not data or 'result' not in data:
                break

            tourneys = data['result']
            if len(tourneys) == 0:
                break

            for t in tourneys:
                # 解析 locations 字段
                locations = t.get('locations')
                prizepool = t.get('prizepool', 0) or 0

                # locations 可能是 dict 或 None
                if isinstance(locations, dict):
                    iso_codes = set()
                    for key, val in locations.items():
                        if key.startswith('country') and isinstance(val, str):
                            iso_codes.add(val.lower())

                    # 匹配到我们的目标国家
                    for country_en, country_iso in COUNTRIES.items():
                        if country_iso in iso_codes:
                            tournament_results[country_en] += 1
                            prizepool_results[country_en] += prizepool

            total_processed += len(tourneys)
            print(f"    已处理 {total_processed} 场比赛...", end='\r')
            page += 1

            if len(tourneys) < 1000:
                break

            time.sleep(DELAY)

        print(f"    完成: {total_processed} 场比赛")

        # 保存中间结果
        df = pd.DataFrame({
            'Country': list(COUNTRIES.keys()),
            'Tournament_Count_Real': [tournament_results[c] for c in COUNTRIES.keys()],
            'PrizePool_Total_Real': [prizepool_results[c] for c in COUNTRIES.keys()]
        })
        df.to_csv('tournaments_raw.csv', index=False, encoding='utf-8-sig')

    print(f"\n  赛事数据采集完成")
    print(f"  中国赛事数: {tournament_results.get('China', 0)}, 中国奖金池: {prizepool_results.get('China', 0):,.0f} USD")
    print(f"  巴西赛事数: {tournament_results.get('Brazil', 0)}, 巴西奖金池: {prizepool_results.get('Brazil', 0):,.0f} USD")

    return tournament_results, prizepool_results


# =============================================================
# Phase 3: 合并到主数据集 + 输出final CSV
# =============================================================
def merge_and_output(player_results, tournament_results, prizepool_results):
    """
    合并Liquipedia真实数据到主数据集，生成最终CSV
    """
    print("\n" + "=" * 60)
    print("  Phase 3: 合并到主数据集")
    print("=" * 60)

    # 构建采集结果DataFrame
    real_data = pd.DataFrame({
        'Country': list(COUNTRIES.keys()),
        'Player_Count_Real': [player_results[c] for c in COUNTRIES.keys()],
        'Tournament_Count_Real': [tournament_results[c] for c in COUNTRIES.keys()],
        'PrizePool_Total_Real': [prizepool_results[c] for c in COUNTRIES.keys()]
    })

    # 加载之前的备用数据集
    master = pd.read_csv('esports_sem_final_with_real.csv')

    # 合并
    df = pd.merge(master, real_data, on='Country', how='left')

    # 计算人均指标
    if 'Population' in df.columns:
        df['PrizePool_per_Capita_Real'] = df['PrizePool_Total_Real'] / df['Population']
        df['Players_per_Million_Real'] = df['Player_Count_Real'] / (df['Population'] / 1e6)

    # 更新复合指标
    if 'Internationalization_Real' in df.columns:
        # 用真实数据重新计算国际化指数
        max_players = df['Player_Count_Real'].max()
        max_tourneys = df['Tournament_Count_Real'].max()
        max_prize = df['PrizePool_Total_Real'].max()

        df['Internationalization_Real_v2'] = (
            0.35 * df['Player_Count_Real'] / max_players +
            0.35 * df['Tournament_Count_Real'] / max_tourneys +
            0.30 * df['PrizePool_Total_Real'] / max_prize
        )

    # 新旧数据对比
    print("\n新旧数据对比：")
    compare_cols = ['Country',
                    'Esports_Tournaments_Count', 'Tournament_Count_Real',
                    'Pro_Players_Count', 'Player_Count_Real',
                    'Esports_PrizePool_MillionUSD', 'PrizePool_Total_Real'
                    ]
    available_cols = [c for c in compare_cols if c in df.columns]
    print(df[available_cols].head(10).to_string(index=False))

    # 保存
    output_path = 'esports_sem_final_liquipedia.csv'
    df.to_csv(output_path, index=False, encoding='utf-8-sig')

    print(f"\n✅ 最终数据集已保存至: {output_path}")
    print(f"   数据集: {len(df)} 个国家 × {len(df.columns)} 个变量")

    # 数据源标注
    real_count = df['Player_Count_Real'].notna().sum()
    print(f"\n数据现状:")
    print(f"  ✅ Player_Count_Real: {real_count}/20 个国家")
    print(f"  ✅ Tournament_Count_Real: {df['Tournament_Count_Real'].notna().sum()}/20")
    print(f"  ✅ PrizePool_Total_Real: {df['PrizePool_Total_Real'].notna().sum()}/20")
    print(f"  ✅ World Bank (宏观变量)")
    print(f"  ✅ Esports Charts (观众数据)")
    print(f"  ✅ Hofstede (文化维度)")
    print(f"  ✅ Liquipedia API (选手/赛事/奖金) ✨NEW")

    return df


# =============================================================
# 主函数
# =============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  LiquipediaDB API v3 数据采集")
    print(f"  目标: {len(COUNTRIES)} 个国家 × {len(GAMES)} 款游戏")
    print("=" * 60)

    total_requests = len(COUNTRIES) * len(GAMES) * 3  # 预估
    print(f"\n  预计API请求数: ~{total_requests}")
    print(f"  预计耗时: ~{total_requests * DELAY / 60:.0f} 分钟\n")

    # Phase 1: 选手
    player_results = collect_players()

    # Phase 2: 赛事
    tournament_results, prizepool_results = collect_tournaments()

    # Phase 3: 合并
    df = merge_and_output(player_results, tournament_results, prizepool_results)

    print("\n" + "=" * 60)
    print("  全部完成！")
    print("  最终文件: esports_sem_final_liquipedia.csv")
    print("=" * 60)
