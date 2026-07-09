import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np, pandas as pd

df = pd.read_csv('esports_sem_final.csv')
df = df[df['Country'] != 'Russia']
df['Int'] = (0.35*df['Player_Count']/df['Player_Count'].max() + 0.35*df['Tournament_Count']/df['Tournament_Count'].max() + 0.30*df['PrizePool_Total']/df['PrizePool_Total'].replace(0,np.nan).max())
df['Com'] = df['Peak_Viewers']/df['Peak_Viewers'].max()
df['UA_r'] = df['UAI'].max()-df['UAI']
df['Cul'] = (0.25*df['IDV']/df['IDV'].max() + 0.25*df['UA_r']/df['UA_r'].max() + 0.25*df['IVR']/df['IVR'].max() + 0.25*df['LTO']/df['LTO'].max())
df['lgdp'] = np.log(df['GDP_per_Capita'].replace(0,np.nan))
df['Tec'] = (0.50*df['Internet_Penetration']/df['Internet_Penetration'].max() + 0.50*df['lgdp']/df['lgdp'].max())
for c in ['Int','Com','Cul','Tec']: df[c+'_z']=(df[c]-df[c].mean())/df[c].std()
lv=df[['Int_z','Com_z','Cul_z','Tec_z']]; lv.columns=['INT','COM','CUL','TEC']; n=len(lv); corr=lv.corr()

HDR,WF='#1B3A5C','white'
R1,R2='#FFFFFF','#ECF0F4'
GR,RED,BLU='#1E6B3C','#B71C1C','#3A6EA5'

# ============================================================
# FIGURE 1 - extra large, boxes not cut, notes way below
# ============================================================
def fig1():
    fig,ax=plt.subplots(figsize=(26,14))
    ax.set_xlim(0,26); ax.set_ylim(0,14); ax.axis('off')
    ax.set_title('Figure 1. Conceptual Path Model (N = 24, Bootstrap 5,000)',fontsize=18,fontweight='bold',pad=30,color=HDR)

    B=lambda x,y,w,h,t,fc='#D3E0ED',ec=HDR,fs=13,tc='#071528':(
        ax.add_patch(mpatches.FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.5',lw=3.5,facecolor=fc,edgecolor=ec)),
        ax.text(x,y,t,ha='center',va='center',fontsize=fs,fontweight='bold',color=tc,linespacing=1.3))

    B(3,11,5.5,3.5,'Cultural Openness\n\nHofstede: IDV, UAI-rev,\nIVR, LTO')
    B(3,2.5,5.5,3.2,'Technological Infrastructure\n\nInternet Penetration,\nlog GDP per Capita')
    B(13,6.5,5.5,3.8,'Esports Internationalization\n\nProfessional Players,\nTournament Hosting,\nPrize Pool Accumulation')
    B(23,6.5,4.0,3.0,'Communication\nEfficacy\n\nAll-Time Peak\nConcurrent Viewers')

    # arrows
    for x1,y1,x2,y2,lb,c in [
        (5.7,10, 20.5,8.5, 'H2: 0.17 n.s.', '#E07000'),
        (5.7,3, 20.5,4.5, 'H3: 0.18 n.s.', '#E07000'),
        (5.7,10.5,10.3,8.3,'H4: 0.08 n.s.', '#6B8E23'),
        (5.7,3, 10.3,4.7, 'H5: -0.13 n.s.', '#6B8E23'),
        (15.8,6.5,21,6.5,  'H1: 0.57**',   HDR),
    ]:
        ax.annotate('',xy=(x2,y2),xytext=(x1,y1),arrowprops=dict(arrowstyle='->',color=c,lw=4,connectionstyle='arc3,rad=0.2'))
        mx,my=(x1+x2)/2,(y1+y2)/2
        if 'H2' in lb: mx+=6
        elif 'H3' in lb: mx+=6; my-=0.5
        elif 'H4' in lb: my-=0.8
        elif 'H5' in lb: my+=0.8
        ax.text(mx,my,lb,ha='center',va='center',fontsize=12,color=c,fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3',facecolor='white',edgecolor=c,alpha=0.95,lw=2))

    ax.text(1,0.3,'R2(COM)=0.42  |  R2(INT)=0.01  |  SRMR=0.75\n** p<.01 (Bootstrap CI excludes zero)  |  n.s.=not significant',fontsize=12,color='#444')
    fig.savefig('Figure1_Path_Model.png',dpi=300,bbox_inches='tight',facecolor='white'); plt.close(fig)
    print('F1')

# ============================================================
# FIGURE 2 - wider canvas, clear horizontal layout, clear arrows
# ============================================================
def fig2():
    fig,ax=plt.subplots(figsize=(26,16))
    ax.set_xlim(-2,28); ax.set_ylim(-1,17); ax.axis('off')
    ax.set_title('Figure 2. Measurement Model: Latent Variable Composites and Indicator Weights',
                 fontsize=18,fontweight='bold',pad=30,color=HDR)

    def B(x,y,w,h,t,fc='#D3E0ED',ec=HDR,fs=12,tc='#071528'):
        ax.add_patch(mpatches.FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.5',lw=3,facecolor=fc,edgecolor=ec))
        ax.text(x,y,t,ha='center',va='center',fontsize=fs,fontweight='bold',color=tc,linespacing=1.2)

    # === TOP ROW: LV1 and LV2 ===
    B(5.5, 13, 7, 4, 'LV1: Esports Internationalization','#D3E0ED',HDR,13,HDR)
    B(20.5,13, 6, 4, 'LV2: Communication\nEfficacy','#D3E0ED',HDR,13,HDR)

    # LV1 indicators below
    for t,x in [('Player Count\n(w=0.35)',2),('Tournament Cnt\n(w=0.35)',5.5),('Prize Pools\n(w=0.30)',9)]:
        B(x,10,3.2,2.0, t,'#E8F5E9','#2E7D32',10,GR)

    # LV2 indicator below
    B(20.5,10,3.2,2.0,'Peak Viewers\n(single ind.)','#E8F5E9','#2E7D32',10,GR)

    # === BOTTOM ROW: LV3 and LV4 ===
    B(5.5,4.5,7,4,'LV3: Cultural Openness','#D3E0ED',GR,13,GR)
    B(20.5,4.5,6,4,'LV4: Technological\nInfrastructure','#D3E0ED','#E07000',13,'#E07000')

    # LV3 indicators below
    for t,x in [('Individualism\n(w=0.25)',2),('UAI-Reversed\n(w=0.25)',5.5),
                ('Indulgence\n(w=0.25)',9)]:
        B(x,1.8,3.2,2.0, t,'#FFF3E0','#E65100',10,'#E07000')

    # LV4 indicators below
    for t,x in [('Internet Pen.\n(w=0.50)',18.5),('log GDP/cap.\n(w=0.50)',22.5)]:
        B(x,1.8,3.2,2.0, t,'#FFF3E0','#E65100',10,'#E07000')

    # === ARROWS with clear labels ===
    # H1: LV1 → LV2 (horizontal, top)
    ax.annotate('',xy=(17.5,13),xytext=(9,13),
                 arrowprops=dict(arrowstyle='->',color=HDR,lw=5))
    ax.text(13.25,14.2,'H1: 0.57**',ha='center',fontsize=13,color=HDR,fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor=HDR,lw=1.5))

    # H2: LV3 → LV2 (top right to bottom right, via right side) ... actually LV3→COM
    # Let me re-read the model:
    # COM ~ INT + CUL + TEC   => H2: CUL→COM, H3: TEC→COM
    # INT ~ CUL + TEC         => H4: CUL→INT, H5: TEC→INT

    # H2: CUL(LV3) → COM(LV2) — diagonal
    ax.annotate('',xy=(18,11),xytext=(8,6.5),
                 arrowprops=dict(arrowstyle='->',color='#E07000',lw=4,connectionstyle='arc3,rad=-0.3'))
    ax.text(15,8,'H2: 0.17 n.s.',ha='center',fontsize=12,color='#E07000',fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor='#E07000',lw=1.5))

    # H3: TEC(LV4) → COM(LV2) — vertical-ish right side
    ax.annotate('',xy=(20.5,11),xytext=(20.5,6.5),
                 arrowprops=dict(arrowstyle='->',color='#E07000',lw=4))
    ax.text(22.8,8.8,'H3: 0.18 n.s.',ha='center',fontsize=12,color='#E07000',fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor='#E07000',lw=1.5))

    # H4: CUL(LV3) → INT(LV1) — left side upward
    ax.annotate('',xy=(5.5,11),xytext=(5.5,6.5),
                 arrowprops=dict(arrowstyle='->',color='#6B8E23',lw=4))
    ax.text(3.2,8.8,'H4: 0.08 n.s.',ha='center',fontsize=12,color='#6B8E23',fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor='#6B8E23',lw=1.5))

    # H5: TEC(LV4) → INT(LV1) — diagonal bottom-right to top-left
    ax.annotate('',xy=(9,11),xytext=(18,6.5),
                 arrowprops=dict(arrowstyle='->',color='#6B8E23',lw=4,connectionstyle='arc3,rad=0.3'))
    ax.text(11,8,'H5: -0.13 n.s.',ha='center',fontsize=12,color='#6B8E23',fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2',facecolor='white',edgecolor='#6B8E23',lw=1.5))

    fig.savefig('Figure2_Measurement_Model.png',dpi=300,bbox_inches='tight',pad_inches=0.3,facecolor='white'); plt.close(fig)
    print('F2')

# ============================================================
# TABLES - wide, big fonts, clearly readable
# ============================================================
def mk_tbl(title,rows,cl,cw,cf,note,fs=14):
    ncols=len(cl); nrows=len(rows); tw=sum(cw)
    h=max(4.5,nrows*0.7+2.0)
    fig,ax=plt.subplots(figsize=(max(16,tw+1.5),h)); ax.axis('off')
    ax.set_title(title,fontsize=15,fontweight='bold',loc='left',pad=15,color=HDR)
    tbl=ax.table(cellText=rows,colLabels=cl,cellLoc='center',loc='center')
    tbl.auto_set_font_size(False); tbl.scale(1.3,2.0)
    for k,c in tbl.get_celld().items():
        c.set_edgecolor('#D0D5DD'); c.set_linewidth(0.5)
        if k[0]==0: c.set_facecolor(HDR); c.set_text_props(color=WF,fontweight='bold',fontsize=fs)
        elif k[0]%2==0: c.set_facecolor(R2)
        else: c.set_facecolor(R1)
        cf(c,k)
        if k[1]==0 and k[0]>0: c.set_text_props(ha='left')
        c.set_text_props(fontsize=fs)
    if note: ax.text(0.5,-0.10,note,fontsize=10,color='#555',ha='center',transform=ax.transAxes)
    return fig,ax

def tab1():
    nm=['1. Internationalization','2. Communication Efficacy','3. Cultural Openness','4. Technological Infrastructure']
    rs=[[nm[i],f'{lv.iloc[:,i].mean():.2f}',f'{lv.iloc[:,i].std():.2f}',f'{lv.iloc[:,i].min():.2f}',f'{lv.iloc[:,i].max():.2f}']+
        [f'{corr.iloc[i,j]:.2f}' if j<=i else '' for j in range(4)] for i in range(4)]
    cl=['Variable','M','SD','Min','Max','1. INT','2. COM','3. CUL','4. TEC']
    def cf(c,k):
        if k[1]>=5 and k[0]>0: c.set_text_props(color=HDR,fontweight='bold')
    fig,ax=mk_tbl('Table 1. Descriptives and Bivariate Correlations (N=24)',rs,cl,
                   [0.40,0.08,0.08,0.08,0.08,0.12,0.12,0.12,0.12],cf,
                   'Note. All variables standardized (z-scores). Pearson r. |r|>.40 significant at p<.05.',14)
    fig.savefig('Table1_Descriptive.png',dpi=300,bbox_inches='tight',pad_inches=0.3,facecolor='white'); plt.close(fig); print('T1')

def tab2():
    rs=[['H1: Internationalization → Communication Efficacy','0.57','[0.36, 1.24]','3.35**','H1','Supported ✓'],
        ['Cultural Openness → Communication Efficacy','0.17','[-0.23, 0.67]','0.78','H2','Not supported'],
        ['Tech. Infrastructure → Communication Efficacy','0.18','[-0.43, 0.76]','0.82','H3','Not supported'],
        ['Cultural Openness → Internationalization','0.08','[-0.41, 0.79]','0.28','H4','Not supported'],
        ['Tech. Infrastructure → Internationalization','-0.13','[-1.11, 0.40]','-0.46','H5','Not supported']]
    cl=['Hypothesized Path','β','Bootstrap 95% CI','t','Hyp.','Result']
    def cf(c,k):
        if k[1]==5 and k[0]>0:
            if '✓' in str(c.get_text()): c.set_facecolor(GR); c.set_text_props(color=WF,fontweight='bold')
            else: c.set_facecolor(RED); c.set_text_props(color=WF,fontweight='bold')
    fig,ax=mk_tbl('Table 2. Path Coefficients, Bootstrap 95% CI, and Hypothesis Tests',rs,cl,
                   [0.42,0.06,0.22,0.08,0.08,0.16],cf,
                   'Note. β=standardized PLS-SEM coefficient. Bootstrap 95% CI from 5,000 resamples.\n** p<.01. R2(COM)=0.42, R2(INT)=0.01. VIF<1.30. SRMR=0.75.',14)
    fig.savefig('Table2_Path_Coefficients.png',dpi=300,bbox_inches='tight',pad_inches=0.3,facecolor='white'); plt.close(fig); print('T2')

def tab3():
    rs=[['Indonesia','0.07','-0.52','+0.59','Mobile-dominant'],
        ['India','-0.13','-0.38','+0.26','Mobile-dominant'],
        ['Thailand','-0.37','-0.44','+0.07','Mixed (mobile+PC)'],
        ['Brazil','0.89','0.85','+0.04','Mixed (mobile+PC)'],
        ['South Korea','1.24','1.36','-0.12','PC-traditional']]
    cl=['Country','6-Game z','4-Game z (PC-only)','Δ','Primary Ecosystem']
    def cf(c,k):
        if k[0]>0:
            if k[1]==0: c.set_facecolor(BLU); c.set_text_props(color=WF,fontweight='bold')
            if k[1]==4:
                v=str(c.get_text())
                if '+0.59' in v: c.set_facecolor(GR); c.set_text_props(color=WF,fontweight='bold')
                elif v.startswith('+') and len(v)>1: c.set_facecolor('#C8E6C9'); c.set_text_props(color='#1B5E20',fontweight='bold')
                elif '-' in v or chr(8722) in v: c.set_facecolor(RED); c.set_text_props(color=WF,fontweight='bold')
    fig,ax=mk_tbl('Table 3. Mobile vs. PC Internationalization Sensitivity',rs,cl,
                   [0.22,0.18,0.26,0.14,0.22],cf,
                   'Note. 6-Game=LoL+VALORANT+Dota2+CS+Mobile Legends+PUBG Mobile. 4-Game excludes mobile titles.',14)
    fig.savefig('Table3_Mobile_Sensitivity.png',dpi=300,bbox_inches='tight',pad_inches=0.3,facecolor='white'); plt.close(fig); print('T3')

fig1(); fig2(); tab1(); tab2(); tab3()
print('Done.')
