import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os
import matplotlib.font_manager as fm
from datetime import date




from matplotlib import font_manager
font_dirs = [os.getcwd()]
font_files = font_manager.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    font_manager.fontManager.addfont(font_file)
import warnings
warnings.filterwarnings("ignore")

sns.set_theme(style='whitegrid', font_scale=1.5)
sns.set_palette('Set2', n_colors=10)
plt.rc('font', family='NanumGothic')
plt.rc('axes', unicode_minus=False)

#Page Setting
st.set_page_config(page_title='OPST Management Price Visualization',
                   page_icon='🐋', layout='wide')
if st.button("새로고침", type = 'secondary'):
    #새로고침 버튼 만들기
    st.experimental_rerun()

st.title("Opst Management Price Visualization")
#APP_TITLE = 'Apartments Management Price Visualization'
APP_SUB_TITLE = '단위: 만원'
#st.set_page_config(APP_TITLE)
#st.title(APP_TITLE)
st.caption(APP_SUB_TITLE)

#Data loading & preprocessing
df = pd.read_csv('OPST_최종.csv', encoding = 'euc-kr', index_col='Unnamed: 0')
dff = df.groupby(['gu']).agg({'cost' : 'mean', 'opst':'count','평수':'median'}).reset_index()
#df.drop(index = list(df[df['address'] == '0'].index), inplace = True)
#df.drop(index = list(df[df['cost'] == 0].index), inplace = True)
#city,gu,dong = [],[],[]
#for i in df['address']:
#    if i != '0':
#        city.append(i.split()[0])
#        gu.append(i.split()[1])
#        dong.append(i.split()[2])
#    else:
#        continue
#df['city'] = city
#df['gu'] = gu
#df['dong'] = dong

#df.groupby(['gu'])[['cost']].mean().plot()


#side bar




my_df = df
st.sidebar.header('위치 선택')

option01 = st.sidebar.multiselect('구 선택',
                                  df['gu'].unique())
check01 = st.sidebar.checkbox("전체 구 선택", value=False)
if check01:
    my_df = df
else:
    my_df = df[df['gu'].isin(option01)]
option02 = st.sidebar.multiselect('동 선택',
                                  my_df['dong'].unique())
check02 = st.sidebar.checkbox("전체 동 선택", value = False)
if check02:
    my_df_1 = my_df
else:
    my_df_1 = my_df[my_df['dong'].isin(option02)]
st.sidebar.warning("🚨필터 적용을 눌러야 보입니다!")
if my_df_1.empty:
  st.sidebar.write("조건을 선택할 수 없습니다!")
else:
  st.sidebar.header('조건 선택')
  op1, op2 = st.sidebar.slider("최소 평 수", round(my_df['평수'].min()),round(my_df['평수'].max()),(1,1))
  st.sidebar.write("적용되는 평수는",op1,"와",op2,"사이 입니다")
  my_df_2 = my_df_1[my_df_1['평수'].between(op1,op2)]
  option04 = st.sidebar.radio("원하는 층 선택",['고층','중층','저층'])
  st.sidebar.write("선택하신 층은 ",option04,"입니다.")
  my_df_2 = my_df_2[my_df_2['floor'] == option04[0]]

start_button = st.sidebar.button(
    "필터 적용📊"
)

if start_button:
    my_df_2 = my_df_2[my_df_2['평수'].between(op1,op2)]
    st.sidebar.success("필터 적용 되었습니다!")
    st.balloons()

import time 

# 방법 1 progress bar 
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
# Update the progress bar with each iteration.
    latest_iteration.text(f'Iteration {i+1}')
    bar.progress(i + 1)
    time.sleep(0.05)
  # 0.05 초 마다 1씩증가
    #st.balloons()
    # 시간 다 되면 풍선 이펙트 보여주기

def first_cost(z):
    fig = plt.figure(figsize=(20, 10))
    ax = sns.barplot(x='gu', y='cost', data=z, palette='pastel', errorbar=None)
    ax = sns.lineplot(x=z['gu'], y=z['cost'].mean(), linewidth=1, color='red', label='서울시 평균 관리비(원)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.text('강남구', z['cost'].mean() - 2000, '%.0f' % z['cost'].mean(), ha='right', va='bottom', size=10)
    fig_path = "first_cost_plot.png"  
    plt.savefig(fig_path)
    plt.close() 
    return fig_path

def first_opst(z):
    fig1 = plt.figure(figsize=(20, 10))
    ax1 = sns.barplot(x='gu', y='opst', data=z, palette='pastel', errorbar=None)
    ax1 = sns.lineplot(x=z['gu'], y=z['opst'].count(), linewidth=1, color='red', label='서울시 평균 오피스텔 매물 수')
    plt.legend()
    plt.xticks(rotation=45)
    plt.text('강남구', z['opst'].mean(), '%.0f' % z['opst'].mean(), ha='right', va='bottom', size=10)
    fig1_path = "first_opst_plot.png" 
    plt.savefig(fig1_path)
    plt.close()  
    return fig1_path
def second_cost(z):
    fig = plt.figure(figsize=(20, 10))
    ax = sns.barplot(x='dong', y='cost', data=z.groupby(['dong'])[['cost']].mean().reset_index(), palette='pastel', errorbar=None)
    ax = sns.lineplot(x=z['dong'], y=z['cost'].mean(), linewidth=1, color='red', label= f"{my_df['gu'].unique().reshape(1,1)[0][0]} 평균 관리비(원)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.text(my_df.index[0], z['cost'].mean() - 2000, '%.0f' % z['cost'].mean(), ha='right', va='bottom', size=10)
    fig_path = "first_cost_plot.png"  
    plt.savefig(fig_path)
    plt.close() 
    return fig_path
            
def second_opst(z):
    fig1 = plt.figure(figsize=(20, 10))
    ax1 = sns.barplot(x='dong', y='opst' ,data = z.groupby(['dong'])[['opst']].count().reset_index(), palette='pastel', errorbar=None)
    plt.xticks(rotation=10)
    fig1_path = "first_opst_plot.png" 
    plt.savefig(fig1_path)
    plt.close()  
    return fig1_path
            

st.header('0. Overview')

#Visualization
if len(option01) == 0:
    #st.set_option('deprecation.showPyplotGlobalUse', False)
    col1, col2 = st.columns(2)
    with col1:
        st.write('구 별 평균 관리비(월)') 
        plot_path1 = first_cost(dff)
        st.image(plot_path1)
    with col2:
        st.write('구 별 오피스텔 매물 수')
        plot_path2 = first_opst(dff)
        st.image(plot_path2)
elif len(option01) > 1:
    st.warning("구를 한 개만 선택해주세요!")
else:
    col1, col2,col3 = st.columns(3)
    col1.metric(label = '구 평균 관리비(단위:만원)', value = round(my_df['cost'].mean() / 10000, 3),
            delta = round(my_df['cost'].mean() / 10000 - df['cost'].mean() / 10000 , 3))
    if len(option02) == 0:
        st.set_option('deprecation.showPyplotGlobalUse', False)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"{my_df['gu'].unique().reshape(1,1)[0][0]}에 속하는 동 별 평균 관리비(원)") 
            plot_path4 = second_cost(my_df)
            st.image(plot_path4)
        with col2:
            st.write(f"{my_df['gu'].unique().reshape(1,1)[0][0]}에 속하는 동 별 오피스텔 매물 수")
            plot_path5 = second_opst(my_df)
            st.image(plot_path5)
            
        st.warning("해당 조건에 맞는 오피스텔이 없습니다!")
        st.warning("조건을 다시 설정 해주세요")
    elif len(option02) > 1:
        st.warning("동을 1개만 선택해주세요!")
    else:
        col2.metric(label = '동 평균 관리비(단위:만원)', value = round(my_df_1['cost'].mean() / 10000, 3),
                    delta = round(my_df['cost'].mean() / 10000 - df['cost'].mean() / 10000, 3))
        my_agg = my_df_1.groupby(['opst'])[['cost']].mean().reset_index().sort_values('cost', ascending=False).head(5)
        fig = plt.figure(figsize=(20,10))
        fig = plt.title(f"{my_df_1['dong'].unique().reshape(1,1)[0][0]} 별 오피스텔 Top 5 평균 관리비(원)")
        ax = sns.barplot(x='opst', y='cost', data=my_agg, palette='pastel')
        fig = plt.xticks(rotation=10)
        fig3_path = "top5_plot.png" 
        plt.savefig(fig3_path)
        plt.close()
        plt_path3 = st.image(fig3_path)
        col3.metric(label = '조건에 맞는 관리비 평균(단위:만원)', value = round(my_df_2['cost'].mean() / 10000, 3),
                      delta = round(my_df_2['cost'].mean() / 10000 - my_df['cost'].mean() / 10000, 3))
        col3.info("조건을 선택해주셔야 보입니다!")
        if my_df_2.empty:
            st.warning("조건을 다시 선택해주세요!")
        else:
            st.subheader('선택한 조건에 맞는 오피스텔 입니다!')
            opst_name = st.selectbox("원하는 오피스텔을 골라주세요", my_df_2['opst'].unique())

            opst = my_df_2[my_df_2['opst'] == opst_name]


            st.text("오피스텔 이름 : {}".format(opst['opst'].unique()))
            st.text("오피스텔 평수 : {}".format(opst['평수'].unique()))
            st.text("오피스텔 층 : {}".format(opst['floor'].unique()))
            st.text("오피스텔 관리비 : {}".format(opst['cost'].unique()))
            st.table(opst)
        
