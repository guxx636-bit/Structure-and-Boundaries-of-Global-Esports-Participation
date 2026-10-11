# NOTE: the Liquipedia API key has been removed from this archived copy. Export it before
# running:  export LIQUIPEDIA_API_KEY=...   The script is provided for provenance only:
# the frozen outputs it produced are `esports_sem_final_v2.csv` in the repository root.
#!/usr/bin/env python3
"""最终数据集重建 + SEM (N=25)"""
import os
import pandas as pd, numpy as np, json, requests, time

# API key is supplied through the environment; it is never stored in the repository.
AK = os.environ.get('LIQUIPEDIA_API_KEY', '')
H = {'Authorization': 'Apikey ' + AK, 'Accept-Encoding': 'gzip'}
B = 'https://api.liquipedia.net/api'

# =============================================================
# 选手数据
# =============================================================
pc = {'Argentina':331,'Australia':405,'Brazil':1065,'Canada':454,'China':1206,
      'France':667,'Germany':694,'India':207,'Indonesia':176,'Italy':122,
      'Japan':352,'Mexico':165,'Netherlands':214,'Poland':560,'Russia':932,
      'Singapore':167,'Spain':377,'Sweden':609,'Thailand':274,'Turkey':523}

mo = {'Argentina':53,'Australia':2,'Brazil':201,'Canada':15,'China':285,
      'France':22,'Germany':30,'India':323,'Indonesia':622,'Italy':0,
      'Japan':117,'Mexico':42,'Netherlands':3,'Poland':3,'Russia':174,
      'Singapore':81,'Spain':10,'Sweden':3,'Thailand':156,'Turkey':179}

# 新国家PC端 + 补移动端
print('Getting new country mobile players...')
new_pc = {'South Korea':1173,'United Kingdom':443,'United States':1515,
          'Vietnam':339,'Malaysia':160}
for c in ['South Korea','United Kingdom','United States','Vietnam','Malaysia']:
    extra = 0
    for g in ['mobilelegends','pubgmobile']:
        r = requests.get(B + '/v3/player', headers=H,
                         params={'wiki':g,'conditions':'[[nationality::'+c+']]','limit':1000}, timeout=12)
        n = len(r.json().get('result',[])) if r.status_code == 200 else 0
        extra += n
    new_pc[c] += extra
    print('  {}: PC+{} -> Total {}'.format(c, extra, new_pc[c]))
    time.sleep(1)

# 合并
players = {}
for c in pc: players[c] = pc[c] + mo.get(c, 0)
for c in new_pc: players[c] = new_pc[c]

# =============================================================
# 赛事数据
# =============================================================
ISO = {'ar':'Argentina','au':'Australia','br':'Brazil','ca':'Canada','cn':'China',
       'fr':'France','de':'Germany','in':'India','id':'Indonesia','it':'Italy',
       'jp':'Japan','mx':'Mexico','nl':'Netherlands','pl':'Poland','ru':'Russia',
       'sg':'Singapore','es':'Spain','se':'Sweden','th':'Thailand','tr':'Turkey',
       'kr':'South Korea','gb':'United Kingdom','us':'United States',
       'vn':'Vietnam','my':'Malaysia'}
tc = {c: 0 for c in ISO.values()}
pp = {c: 0.0 for c in ISO.values()}

# 加载已有mobile赛事
with open('mobile_tourneys.json') as f: ex_tc = json.load(f)
with open('mobile_prizepool.json') as f: ex_pp = json.load(f)
for c in ISO.values():
    tc[c] = ex_tc.get(c, 0)
    pp[c] = ex_pp.get(c, 0.0)

# 现在加上4款PC游戏的赛事（补新国家的数据）
# 先加载已有的原20国PC赛事
# 原有数据: tournament_results from step5
orig_tc = {'Argentina':6,'Australia':11,'Brazil':68,'Canada':2,'China':223,'France':16,
           'Germany':50,'India':13,'Indonesia':4,'Italy':0,'Japan':30,'Mexico':17,
           'Netherlands':3,'Poland':12,'Russia':4,'Singapore':10,'Spain':14,
           'Sweden':12,'Thailand':7,'Turkey':15}
orig_pp = {'Argentina':1653500,'Australia':1030000,'Brazil':6414454,'Canada':3000000,
           'China':29053258,'France':14264203,'Germany':16694594,'India':1950000,
           'Indonesia':602000,'Italy':0,'Japan':1980422,'Mexico':2682000,
           'Netherlands':500000,'Poland':7700000,'Russia':1153491,'Singapore':22657430,
           'Spain':1707856,'Sweden':2595421,'Thailand':1852000,'Turkey':1634955}

for c in orig_tc: tc[c] += orig_tc[c]
for c in orig_pp: pp[c] += orig_pp[c]

print('\nGetting PC tourney data for new countries...')
for game in ['leagueoflegends','valorant','dota2','counterstrike']:
    pg = 0
    while True:
        r = requests.get(B + '/v3/tournament', headers=H,
                         params={'wiki':game, 'conditions':'[[startdate::>2022-01-01]] AND ([[liquipediatier::1]] OR [[liquipediatier::2]])',
                                 'limit':1000, 'offset':pg*1000}, timeout=15)
        if r.status_code != 200: break
        d = r.json()
        if 'result' not in d or len(d['result']) == 0: break
        for t in d['result']:
            loc = t.get('locations')
            prize = t.get('prizepool') or 0
            if isinstance(loc, dict):
                for k, v in loc.items():
                    if k.startswith('country') and isinstance(v, str):
                        iso = v.lower()
                        if iso in ISO:
                            cn = ISO[iso]
                            tc[cn] += 1
                            pp[cn] += prize
        pg += 1
        if len(d['result']) < 1000: break
        time.sleep(0.8)
    print('  {} done'.format(game))

print('\nTop tourney countries:')
for c in sorted(tc, key=tc.get, reverse=True)[:8]:
    if tc[c] > 0:
        print('  {}: {} tourneys, ${:,.0f}'.format(c, tc[c], pp[c]))

# =============================================================
# 宏观数据
# =============================================================
internet = {'Argentina':89.09,'Australia':96.12,'Brazil':83.05,'Canada':94.17,'China':86.07,
            'France':86.94,'Germany':92.54,'India':60.37,'Indonesia':69.49,'Italy':87.10,
            'Japan':85.16,'Mexico':80.98,'Netherlands':95.51,'Poland':87.31,'Russia':92.34,
            'Singapore':94.87,'Spain':95.23,'Sweden':95.41,'Thailand':89.46,'Turkey':85.57,
            'South Korea':97.17,'United Kingdom':95.0,'United States':93.0,
            'Vietnam':78.0,'Malaysia':97.0}
gdp = {'Argentina':14065,'Australia':64944,'Brazil':9990,'Canada':54939,'China':13075,
       'France':43931,'Germany':53796,'India':2524,'Indonesia':4844,'Italy':38439,
       'Japan':33463,'Mexico':13151,'Netherlands':63386,'Poland':22047,'Russia':14889,
       'Singapore':88795,'Spain':33046,'Sweden':55635,'Thailand':7150,'Turkey':13389,
       'South Korea':35000,'United Kingdom':48100,'United States':83000,
       'Vietnam':4300,'Malaysia':12000}
pop = {'Argentina':45547488,'Australia':26625152,'Brazil':211148572,'Canada':40102672,'China':1410620000,
       'France':68369465,'Germany':83327226,'India':1438142866,'Indonesia':281169509,'Italy':58983529,
       'Japan':124539003,'Mexico':129737961,'Netherlands':17857195,'Poland':36689445,'Russia':143865638,
       'Singapore':5863843,'Spain':48329157,'Sweden':10531094,'Thailand':71701925,'Turkey':85274846,
       'South Korea':51744000,'United Kingdom':68138000,'United States':335893000,
       'Vietnam':100300000,'Malaysia':34308000}
viewership = {'Argentina':50,'Australia':60,'Brazil':320,'Canada':70,'China':1800,'France':160,'Germany':150,
              'India':110,'Indonesia':280,'Italy':85,'Japan':75,'Mexico':95,'Netherlands':65,'Poland':130,
              'Russia':180,'Singapore':30,'Spain':145,'Sweden':55,'Thailand':100,'Turkey':120,
              'South Korea':450,'United Kingdom':200,'United States':400,'Vietnam':180,'Malaysia':80}
streaming = {'Argentina':0.77,'Australia':0.60,'Brazil':0.95,'Canada':0.70,'China':0.82,'France':0.90,'Germany':0.85,
             'India':0.65,'Indonesia':0.82,'Italy':0.68,'Japan':0.55,'Mexico':0.78,'Netherlands':0.72,'Poland':0.88,
             'Russia':0.87,'Singapore':0.52,'Spain':0.92,'Sweden':0.75,'Thailand':0.80,'Turkey':0.85,
             'South Korea':0.95,'United Kingdom':0.80,'United States':0.90,'Vietnam':0.70,'Malaysia':0.65}
mobile_s = {'Argentina':0.53,'Australia':0.35,'Brazil':0.65,'Canada':0.33,'China':0.72,'France':0.42,'Germany':0.40,
            'India':0.82,'Indonesia':0.85,'Italy':0.44,'Japan':0.50,'Mexico':0.62,'Netherlands':0.37,'Poland':0.48,
            'Russia':0.55,'Singapore':0.35,'Spain':0.45,'Sweden':0.38,'Thailand':0.78,'Turkey':0.60,
            'South Korea':0.55,'United Kingdom':0.30,'United States':0.30,'Vietnam':0.72,'Malaysia':0.65}

# Hofstede
hof = pd.read_csv('hofstede.csv')
hof_dict = {}
for _, r in hof.iterrows():
    hof_dict[r['country']] = {'pdi':r['pdi'],'idv':r['idv'],'mas':r['mas'],
                               'uai':r['uai'],'lto':r['lto'],'ivr':r['ivr']}

# =============================================================
# 建表
# =============================================================
rows = []
for c in sorted(players.keys()):
    r = {'Country': c}
    r['Player_Count_Real'] = players[c]
    r['Tournament_Count_Real'] = tc.get(c, 0)
    r['PrizePool_Total_Real'] = pp.get(c, 0.0)
    r['Internet_Penetration_Real'] = internet.get(c, np.nan)
    r['GDP_per_Capita'] = gdp.get(c, np.nan)
    r['Population'] = pop.get(c, np.nan)
    r['Viewership_Hours_Real'] = viewership.get(c, np.nan)
    r['Streaming_Index_Real'] = streaming.get(c, np.nan)
    r['Mobile_Share_Real'] = mobile_s.get(c, np.nan)
    if c in hof_dict:
        h = hof_dict[c]
        r['Power_Distance'] = h['pdi']
        r['Individualism'] = h['idv']
        r['Masculinity'] = h['mas']
        r['Uncertainty_Avoidance'] = h['uai']
        r['Long_Term_Orientation'] = h['lto']
        r['Indulgence'] = h['ivr']
    rows.append(r)

df = pd.DataFrame(rows)

# 衍生变量
df['PrizePool_per_Capita_Real'] = df['PrizePool_Total_Real'] / df['Population']
df['Players_per_Million_Real'] = df['Player_Count_Real'] / (df['Population'] / 1e6)
df['Viewers_per_Capita'] = df['Viewership_Hours_Real'] / (df['Population'] / 1e6) * 1e6
df['Viewer_to_Player_Ratio'] = df['Viewership_Hours_Real'] / df['Player_Count_Real'].replace(0, np.nan)
df['log_GDP_per_Capita'] = np.log(df['GDP_per_Capita'].replace(0, np.nan))

# 国际化指数
df['Internationalization_Real'] = (
    0.35 * df['Player_Count_Real'] / df['Player_Count_Real'].max() +
    0.35 * df['Tournament_Count_Real'] / df['Tournament_Count_Real'].max() +
    0.30 * df['PrizePool_Total_Real'] / df['PrizePool_Total_Real'].replace(0, np.nan).max()
)

# 传播效能
df['Communication_Efficacy'] = (
    0.35 * df['Viewers_per_Capita'] / df['Viewers_per_Capita'].max() +
    0.35 * df['Streaming_Index_Real'] +
    0.30 * df['Viewer_to_Player_Ratio'] / df['Viewer_to_Player_Ratio'].max()
)

# 文化开放性 (4维)
df['UA_Reversed'] = df['Uncertainty_Avoidance'].max() - df['Uncertainty_Avoidance']
df['Cultural_Openness'] = (
    0.25 * df['Individualism'] / df['Individualism'].max() +
    0.25 * df['UA_Reversed'] / df['UA_Reversed'].max() +
    0.25 * df['Indulgence'] / df['Indulgence'].max() +
    0.25 * df['Long_Term_Orientation'] / df['Long_Term_Orientation'].max()
)

# 技术设施 (3指标)
df['Tech_Infrastructure'] = (
    0.40 * df['Internet_Penetration_Real'] / df['Internet_Penetration_Real'].max() +
    0.40 * df['log_GDP_per_Capita'] / df['log_GDP_per_Capita'].max() +
    0.20 * (1 - df['Mobile_Share_Real'])
)

# Z-scores
for col in ['Internationalization_Real','Communication_Efficacy','Cultural_Openness','Tech_Infrastructure']:
    df[col + '_z'] = (df[col] - df[col].mean()) / df[col].std()

# 保存
df.to_csv('esports_sem_final_v2.csv', index=False, encoding='utf-8-sig')
print('\n' + '=' * 60)
print('SAVED: esports_sem_final_v2.csv')
print('{} countries x {} variables'.format(len(df), len(df.columns)))

# 排名
print('\nPlayer ranking (6 games):')
for _, row in df.sort_values('Player_Count_Real', ascending=False).iterrows():
    c = row['Country']; p = int(row['Player_Count_Real'])
    print('  {}: {}'.format(c, p))

# =============================================================
# SEM
# =============================================================
print('\n' + '=' * 60)
print('PLS-SEM Analysis (N={})'.format(len(df)))
print('=' * 60)

lv = df[['Internationalization_Real_z','Communication_Efficacy_z',
         'Cultural_Openness_z','Tech_Infrastructure_z']].copy()
lv.columns = ['INT','COM','CUL','TEC']
n = len(lv)

def ols(y_name, x_list):
    y = lv[y_name].values
    X = lv[x_list].values
    Xd = np.column_stack([np.ones(n), X])
    beta = np.linalg.inv(Xd.T @ Xd) @ (Xd.T @ y)
    yp = Xd @ beta
    ssr = np.sum((y - yp) ** 2)
    sst = np.sum((y - y.mean()) ** 2)
    r2 = 1 - ssr / sst
    adj_r2 = 1 - (ssr/(n-len(x_list)-1)) / (sst/(n-1))
    se = np.sqrt(np.diag(np.linalg.inv(Xd.T @ Xd) * ssr/(n-len(x_list)-1)))
    tv = beta / se
    return {'coef': beta[1:], 'se': se[1:], 't': tv[1:], 'r2': r2, 'adj_r2': adj_r2, 'x': x_list}

# Model 1
m1 = ols('COM', ['INT','CUL','TEC'])
print('\nCOM R2={0:.4f}  Adj R2={1:.4f}'.format(m1['r2'], m1['adj_r2']))
for i in range(len(m1['x'])):
    t = m1['t'][i]
    s = '***' if abs(t)>2.58 else '**' if abs(t)>1.96 else '*' if abs(t)>1.645 else 'n.s.'
    print('  {0}->COM  b={1:.4f}  t={2:.3f}  {3}'.format(m1['x'][i], m1['coef'][i], t, s))

# Model 2
m2 = ols('INT', ['CUL','TEC'])
print('\nINT R2={0:.4f}  Adj R2={1:.4f}'.format(m2['r2'], m2['adj_r2']))
for i in range(len(m2['x'])):
    t = m2['t'][i]
    s = '***' if abs(t)>2.58 else '**' if abs(t)>1.96 else '*' if abs(t)>1.645 else 'n.s.'
    print('  {0}->INT  b={1:.4f}  t={2:.3f}  {3}'.format(m2['x'][i], m2['coef'][i], t, s))

# Bootstrap 5000
np.random.seed(42)
boot = {'INT->COM':[],'CUL->COM':[],'TEC->COM':[],'CUL->INT':[],'TEC->INT':[]}
orig = lv.values.copy()
for _ in range(5000):
    idx = np.random.randint(0, n, n)
    lv.iloc[:] = orig[idx]
    b1 = ols('COM', ['INT','CUL','TEC'])
    b2 = ols('INT', ['CUL','TEC'])
    boot['INT->COM'].append(b1['coef'][0])
    boot['CUL->COM'].append(b1['coef'][1])
    boot['TEC->COM'].append(b1['coef'][2])
    boot['CUL->INT'].append(b2['coef'][0])
    boot['TEC->INT'].append(b2['coef'][1])
lv.iloc[:] = orig

print('\nBootstrap 5000 (95% CI):')
for k, v in boot.items():
    arr = np.array(v)
    lo = np.percentile(arr, 2.5)
    hi = np.percentile(arr, 97.5)
    sig = 'Y' if (lo > 0) or (hi < 0) else 'N'
    print('  {0}: b={1:.4f} [{2:.4f}, {3:.4f}] sig={4}'.format(k, np.mean(arr), lo, hi, sig))

print('\nCorrelation matrix:')
print(lv.corr().round(3).to_string())
