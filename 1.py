Python 3.14.5 (v3.14.5:5607950ef23, May 10 2026, 07:38:09) [Clang 21.0.0 (clang-2100.0.123.102)] on darwin
Enter "help" below or click "Help" above for more information.
"""
生成论文A全部图表 (Figure 1-2, Table 1-3)
需要: pip install matplotlib pandas numpy
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# ============================================================
# Load data
# ============================================================
df = pd.read_csv('esports_sem_final.csv')
df = df[df['Country'] != 'Russia']

# Recompute LV scores
df['Int'] = (0.35 * df['Player_Count'] / df['Player_Count'].max() +
             0.35 * df['Tournament_Count'] / df['Tournament_Count'].max() +
             0.30 * df['PrizePool_Total'] / df['PrizePool_Total'].replace(0, np.nan).max())
df['Com'] = df['Peak_Viewers'] / df['Peak_Viewers'].max()
df['UA_r'] = df['UAI'].max() - df['UAI']
df['Cul'] = (0.25 * df['IDV'] / df['IDV'].max() +
             0.25 * df['UA_r'] / df['UA_r'].max() +
             0.25 * df['IVR'] / df['IVR'].max() +
             0.25 * df['LTO'] / df['LTO'].max())
df['lgdp'] = np.log(df['GDP_per_Capita'].replace(0, np.nan))
df['Tec'] = (0.50 * df['Internet_Penetration'] / df['Internet_Penetration'].max() +
             0.50 * df['lgdp'] / df['lgdp'].max())

for c in ['Int', 'Com', 'Cul', 'Tec']:
    df[c + '_z'] = (df[c] - df[c].mean()) / df[c].std()

lv = df[['Int_z', 'Com_z', 'Cul_z', 'Tec_z']]
lv.columns = ['INT', 'COM', 'CUL', 'TEC']
n = len(lv)
corr = lv.corr()

print(f'Data loaded: N={n}')


# ============================================================
# FIGURE 1: Conceptual Path Model
# ============================================================
def draw_figure1():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title('Figure 1. Conceptual Path Model (N = 24, Bootstrap 5,000)',
                 fontsize=13, fontweight='bold', pad=15)

    boxes = {
        'CUL': (1.5, 5, 'Cultural Openness\nHofstede: IDV, UAI-rev, IVR, LTO'),
        'TEC': (1.5, 2, 'Technological\nInfrastructure\nInternet %, log GDP'),
        'INT': (6, 3.5, 'Esports\nInternationalization\nPlayers, Tournaments,\nPrize Pools'),
        'COM': (10, 3.5, 'Communication\nEfficacy\nPeak Viewers'),
    }

    for key, (x, y, label) in boxes.items():
        rect = mpatches.FancyBboxPatch(
            (x - 1.5, y - 1.2), 3, 2.4,
            boxstyle="round,pad=0.15",
            facecolor='#D6E4F0', edgecolor='#2F5496', linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=9,
                fontweight='bold', color='#2F5496')

    # Arrows: (x1, y1, x2, y2, label, color)
    arrows = [
        (1.5, 3.8, 8.5, 3.8, 'H2: 0.17 n.s.', '#C55A11'),
        (1.5, 2.3, 8.5, 3.0, 'H3: 0.18 n.s.', '#C55A11'),
        (3, 5, 4.5, 4, 'H4: 0.08 n.s.', '#548235'),
        (3, 2, 4.5, 3, 'H5: -0.13 n.s.', '#548235'),
        (7.5, 3.5, 8.5, 3.5, 'H1: 0.57**', '#2F5496'),
    ]

    for x1, y1, x2, y2, label, color in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color=color, lw=2.5,
                                     connectionstyle='arc3,rad=0.15'))
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 - 0.2, label,
                ha='center', va='top', fontsize=8, color=color, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.1', facecolor='white',
                          edgecolor='none', alpha=0.85))

    # Footer
    ax.text(0.3, 0.6, 'R2(COM)=0.42  R2(INT)=0.01  SRMR=0.75',
            fontsize=8, color='#666',
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='#CCC'))
    ax.text(0.3, 0.25, '** p < .01; n.s. = not significant',
            fontsize=8, color='#666')

    fig.savefig('Figure1_Path_Model.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('✓ Figure 1 saved')


# ============================================================
# FIGURE 2: Measurement Model
# ============================================================
def draw_figure2():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title('Figure 2. Measurement Model: Latent Variable Composites',
                 fontsize=13, fontweight='bold', pad=15)

    # LV boxes
    lvs = [
        ('LV1: Esports\nInternationalization', 2, 5.5, '#2F5496'),
        ('LV2: Communication\nEfficacy', 11.5, 5.5, '#2F5496'),
        ('LV3: Cultural\nOpenness', 2, 2, '#548235'),
        ('LV4: Technological\nInfrastructure', 11.5, 2, '#C55A11'),
    ]
    for label, x, y, color in lvs:
        rect = mpatches.FancyBboxPatch(
            (x - 2.2, y - 1), 4.4, 2,
            boxstyle="round,pad=0.12",
            facecolor='#D6E4F0', edgecolor=color, linewidth=2
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=10,
                fontweight='bold', color=color)

    # LV1 indicators
    indicators_lv1 = [
        ('Player Count\n(w=0.35)', 0.3, 3.8),
        ('Tournament Count\n(w=0.35)', 2, 3.8),
        ('Prize Pools\n(w=0.30)', 3.7, 3.8),
    ]
    for label, x, y in indicators_lv1:
        rect = mpatches.FancyBboxPatch(
            (x - 1.3, y - 0.6), 2.6, 1.2,
            boxstyle="round,pad=0.08",
            facecolor='#E2EFDA', edgecolor='#548235', linewidth=1
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=7.5, color='#548235')
        ax.annotate('', xy=(2, 4.5), xytext=(x, y + 0.6),
                     arrowprops=dict(arrowstyle='->', color='#548235', lw=1, alpha=0.5))

    # LV2 single indicator
    rect = mpatches.FancyBboxPatch(
        (10.2, 3.2), 2.6, 1.2,
        boxstyle="round,pad=0.08",
        facecolor='#E2EFDA', edgecolor='#548235', linewidth=1
    )
    ax.add_patch(rect)
    ax.text(11.5, 3.8, 'Peak Viewers\n(single indicator)',
            ha='center', va='center', fontsize=7.5, color='#548235')
    ax.annotate('', xy=(11.5, 4.5), xytext=(11.5, 4.4),
                 arrowprops=dict(arrowstyle='->', color='#548235', lw=1, alpha=0.5))

    # LV3 indicators
    indicators_lv3 = [
        ('Individualism\n(w=0.25)', 0.2, 0.5),
        ('UAI-Reversed\n(w=0.25)', 1.3, 0.5),
        ('Indulgence\n(w=0.25)', 2.4, 0.5),
        ('Long-Term\nOrientation\n(w=0.25)', 3.7, 0.5),
    ]
    for label, x, y in indicators_lv3:
        rect = mpatches.FancyBboxPatch(
            (x - 0.9, y - 0.6), 1.8, 1.2,
            boxstyle="round,pad=0.08",
            facecolor='#FDE9D9', edgecolor='#C55A11', linewidth=1
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=6.5, color='#C55A11')
        ax.annotate('', xy=(2, 1), xytext=(x, y + 0.6),
                     arrowprops=dict(arrowstyle='->', color='#C55A11', lw=1, alpha=0.5))

    # LV4 indicators
    indicators_lv4 = [
        ('Internet Penetration\n(w=0.50)', 10.1, 0.5),
        ('log GDP per capita\n(w=0.50)', 12.9, 0.5),
    ]
    for label, x, y in indicators_lv4:
        rect = mpatches.FancyBboxPatch(
            (x - 1.1, y - 0.7), 2.2, 1.4,
            boxstyle="round,pad=0.08",
            facecolor='#FDE9D9', edgecolor='#C55A11', linewidth=1
        )
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=6.5, color='#C55A11')
        ax.annotate('', xy=(11.5, 1), xytext=(x, y + 0.7),
                     arrowprops=dict(arrowstyle='->', color='#C55A11', lw=1, alpha=0.5))

    # Structural paths between LVs
    paths = [
        (6.5, 6.5, 9.5, 6.5, 'H1', '#2F5496', 2),
        (2, 4, 2.5, 2.5, 'H4', '#888', 1.5),
        (2, 3.5, 2.5, 2.5, 'H5', '#888', 1.5),
        (6.5, 4, 9.5, 4, 'H2', '#888', 1.5),
        (6.5, 2.5, 9.5, 2.2, 'H3', '#888', 1.5),
    ]
    for x1, y1, x2, y2, label, color, lw in paths:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                     arrowprops=dict(arrowstyle='->', color=color, lw=lw))
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.15, label,
                ha='center', fontsize=8, color=color, fontweight='bold')

    fig.savefig('Figure2_Measurement_Model.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('✓ Figure 2 saved')


# ============================================================
# TABLE 1: Descriptive Statistics
# ============================================================
def draw_table1():
    fig, ax = plt.subplots(figsize=(9.5, 3.2))
    ax.axis('off')
    ax.set_title('Table 1. Descriptive Statistics and Bivariate Correlations (N = 24)',
                 fontsize=12, fontweight='bold', loc='left', pad=10)

    names = ['1. Internationalization', '2. Communication Efficacy',
             '3. Cultural Openness', '4. Technological Infrastructure']
    data = []
    for i, nm in enumerate(names):
        row = [nm,
               f'{lv.iloc[:, i].mean():.2f}',
               f'{lv.iloc[:, i].std():.2f}',
               f'{lv.iloc[:, i].min():.2f}',
               f'{lv.iloc[:, i].max():.2f}']
        for j in range(4):
            row.append(f'{corr.iloc[i, j]:.2f}' if j <= i else '—')
        data.append(row)

    col_labels = ['Variable', 'M', 'SD', 'Min', 'Max',
                  '1. INT', '2. COM', '3. CUL', '4. TEC']
    tbl = ax.table(cellText=data, colLabels=col_labels, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.0, 1.8)

    for key, cell in tbl.get_celld().items():
        cell.set_edgecolor('white')
        if key[0] == 0:
            cell.set_facecolor('#2F5496')
            cell.set_text_props(color='white', fontweight='bold')
        elif key[0] % 2 == 0:
            cell.set_facecolor('#F2F2F2')
        if key[1] >= 5:
            cell.set_text_props(color='#2F5496', fontweight='bold')

    ax.text(0.5, -0.15,
            'Note. All variables are standardized (z-scores). |r| > .40, p < .05 (two-tailed).',
            fontsize=8, color='#666', ha='center', transform=ax.transAxes)

    fig.savefig('Table1_Descriptive.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('✓ Table 1 saved')


# ============================================================
# TABLE 2: Path Coefficients
# ============================================================
def draw_table2():
    fig, ax = plt.subplots(figsize=(11, 3.8))
    ax.axis('off')
    ax.set_title('Table 2. Path Coefficients, Bootstrap 95% CI, and Hypothesis Tests',
                 fontsize=12, fontweight='bold', loc='left', pad=10)

    d2 = [
        ['H1: INT → COM', '0.57', '[0.36, 1.24]', '3.35**', 'H1', 'Yes ✓'],
        ['H2: CUL → COM', '0.17', '[−0.23, 0.67]', '0.78', 'H2', 'No'],
        ['H3: TEC → COM', '0.18', '[−0.43, 0.76]', '0.82', 'H3', 'No'],
        ['H4: CUL → INT', '0.08', '[−0.41, 0.79]', '0.28', 'H4', 'No'],
        ['H5: TEC → INT', '−0.13', '[−1.11, 0.40]', '−0.46', 'H5', 'No'],
    ]

    col_labels = ['Path', 'β', 'Bootstrap 95% CI', 't', 'Hypothesis', 'Supported']
    tbl = ax.table(cellText=d2, colLabels=col_labels, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.0, 2.2)

    for key, cell in tbl.get_celld().items():
        cell.set_edgecolor('white')
        if key[0] == 0:
            cell.set_facecolor('#2F5496')
            cell.set_text_props(color='white', fontweight='bold')
        elif key[1] == 5 and '✓' in str(cell.get_text()):
            cell.set_facecolor('#E2EFDA')
            cell.set_text_props(color='#548235', fontweight='bold')
        elif key[1] == 5:
            cell.set_facecolor('#FDE9D9')
            cell.set_text_props(color='#C55A11')
        elif key[0] % 2 == 0:
            cell.set_facecolor('#F2F2F2')

    ax.text(0.5, 0.02,
            'Note. β = standardized PLS-SEM coefficient. Bootstrap 95% CI from 5,000 resamples.\n'
            '** p < .01. R²(COM) = 0.42, R²(INT) = 0.01. VIFs < 1.30. SRMR = 0.75.',
            fontsize=8, color='#666', ha='center', transform=ax.transAxes)

    fig.savefig('Table2_Path_Coefficients.png', dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('✓ Table 2 saved')


# ============================================================
# TABLE 3: Mobile vs PC Sensitivity
# ============================================================
def draw_table3():
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.axis('off')
    ax.set_title('Table 3. Sensitivity of Internationalization z-scores to Mobile Game Inclusion',
                 fontsize=12, fontweight='bold', loc='left', pad=10)

    d3 = [
        ['Indonesia', '0.07', '−0.52', '+0.59', 'Mobile-dominant'],
        ['India', '−0.13', '−0.38', '+0.26', 'Mobile-dominant'],
        ['Thailand', '−0.37', '−0.44', '+0.07', 'Mixed (mobile+PC)'],
        ['Brazil', '0.89', '0.85', '+0.04', 'Mixed (mobile+PC)'],
        ['South Korea', '1.24', '1.36', '−0.12', 'PC-traditional'],
    ]

    col_labels = ['Country', '6-Game z', '4-Game z (PC-only)', 'Δ', 'Primary Ecosystem']
    tbl = ax.table(cellText=d3, colLabels=col_labels, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(10)
    tbl.scale(1.0, 2.2)

    for key, cell in tbl.get_celld().items():
        cell.set_edgecolor('white')
        if key[0] == 0:
...             cell.set_facecolor('#2F5496')
...             cell.set_text_props(color='white', fontweight='bold')
...         if key[1] == 4:
...             v = str(cell.get_text())
...             try:
...                 fv = float(v)
...                 if fv >= 0.5:
...                     cell.set_facecolor('#E2EFDA')
...                     cell.set_text_props(color='#548235', fontweight='bold')
...                 elif fv < 0:
...                     cell.set_facecolor('#FDE9D9')
...                     cell.set_text_props(color='#C55A11', fontweight='bold')
...             except:
...                 pass
...         elif key[0] % 2 == 0:
...             cell.set_facecolor('#F2F2F2')
... 
...     ax.text(0.5, 0.02,
...             'Note. 6-Game includes LoL, VALORANT, Dota 2, CS, Mobile Legends, and PUBG Mobile.\n'
...             '4-Game (PC-only) excludes mobile titles. Positive Δ = mobile inclusion raises Internationalization.',
...             fontsize=8, color='#666', ha='center', transform=ax.transAxes)
... 
...     fig.savefig('Table3_Mobile_Sensitivity.png', dpi=200, bbox_inches='tight', facecolor='white')
...     plt.close(fig)
...     print('✓ Table 3 saved')
... 
... 
... # ============================================================
... # RUN
... # ============================================================
... if __name__ == '__main__':
...     draw_figure1()
...     draw_figure2()
...     draw_table1()
...     draw_table2()
...     draw_table3()
