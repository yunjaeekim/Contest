import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_folium import st_folium 
import folium
from folium import plugins
import json
from datetime import date
from sklearn.preprocessing import StandardScaler 
import time
import branca.colormap as cmp

# 서울 행정동 json 파일, seoul_map 설정

jpath = 'seoul_geo.json'
seoul_geo = json.load(open(jpath, encoding = 'utf-8'))
seoul_map = folium.Map(
                    location = [37.5642135, 127.0016985], 
                    tiles = 'cartoDB positron', 
                    zoom_start = 10.5
                    )

# 지하철역 json 파일 로드

with open('station_coordinate.json', encoding='utf-8') as f:
    a = json.loads(f.read())
js = pd.DataFrame(a)
js = js.drop(columns = ['line', 'code'], axis=1)
js = js.rename(columns = {'lat' : '위도', 'lng' : '경도', 'name' : '지하철역'})
js = js.drop_duplicates().reset_index(drop=True)

# -------------------------------------------------------------------------------------

# 서울 생활인구 데이터 (누적) Stremalit 설정

st.set_page_config(page_title='Seoul Map', layout='centered')
st.sidebar.title("서울 생활인구 데이터 (누적)")
st.sidebar.header("시간대 조건")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_time = st.slider("시작시간", 0, 22, 0, 1, key=1)  # 0부터 22까지의 값을 선택할 수 있는 슬라이더

with col2:
    end_time = st.slider("종료시간", 1, 23, 1, 1, key=2)  # 1부터 23까지의 값을 선택할 수 있는 슬라이더

# 서울 생활인구 데이터 (누적) 전처리

living = pd.read_csv('생활인구_groupby.csv', encoding = 'cp949')
scaler = StandardScaler()
living['풋살인구'] = scaler.fit_transform(living[['풋살인구']])

dfs = []
for i in range(start_time, end_time + 1):
    temp_df = living[living['시간대'] == i]
    if not temp_df.empty:
        dfs.append(temp_df)

f1 = folium.FeatureGroup(name='생활인구 데이터 (누적)')
seoul_map.add_child(f1)

for i in range(start_time, end_time + 1):
    fg = plugins.FeatureGroupSubGroup(f1, f'생활인구_{i}')
    seoul_map.add_child(fg)
    locals()['fg' + str(i)] = fg

# 서울 생활인구 데이터 (누적) folium 설정

for i, df_temp in enumerate(dfs):
    living_population = folium.Choropleth(geo_data=seoul_geo,
                             data=df_temp,
                             columns=['행정동명', '풋살인구'],
                             key_on='feature.properties.adm_nm',
                             fill_color='YlOrRd',
                             fill_opacity=0.7,
                             line_opacity=0.3,
                             overlay=False,
                             show=True,
                             legend_name='생활인구수',
                             highlight=True
                             ).geojson.add_to(locals()['fg' + str(i+start_time)])  # fg 변수에 추가
    
    living_population.zoom_on_click = False
    living_population.add_child(folium.features.GeoJsonTooltip(['adm_nm'], labels=False))

# -------------------------------------------------------------------------------------

# 서울 생활인구 데이터 (평균) Streamlit 설정

st.sidebar.title("서울 생활인구 데이터 (평균)")
st.sidebar.header("시간대 조건")
col3, col4 = st.sidebar.columns(2)
with col3:
    start_time = st.slider("시작시간", 0, 22, 0, 1, key=3)  # 0부터 22까지의 값을 선택할 수 있는 슬라이더

with col4:
    end_time = st.slider("종료시간", 1, 23, 1, 1, key=4)  # 1부터 23까지의 값을 선택할 수 있는 슬라이더

# 서울 생활인구 데이터 (평균) 전처리

living = pd.read_csv('생활인구_groupby.csv', encoding = 'cp949')

dfs = []
for i in range(start_time, end_time + 1):
    temp_df = living[living['시간대'] == i]
    if not temp_df.empty:
        dfs.append(temp_df)

f3 = folium.FeatureGroup(name='생활인구 데이터 (평균)')
seoul_map.add_child(f3)

concatenated_df = dfs[0]    
for i, df in enumerate(dfs[1:], start=1):
    suffixes = [f'_{i-1}', f'_{i}']
    concatenated_df = pd.merge(concatenated_df, df, on='행정동명', suffixes=suffixes)

concatenated_df = concatenated_df.rename(columns={'풋살인구': '풋살인구_'+str(len(dfs[1:])), '시간대': '시간대_'+str(len(dfs[1:]))})
cols_to_sum = [f'풋살인구_{i}' for i in range(len(dfs))]
concatenated_df['풋살인구합계'] = concatenated_df[cols_to_sum].mean(axis=1)
cols_to_drop = [col for col in concatenated_df.columns if '풋살인구_' in col or '시간대' in col]
concatenated_df = concatenated_df.drop(columns=cols_to_drop)

#scaler = StandardScaler()
#data = concatenated_df['풋살인구합계'].values.reshape(-1, 1)
#scaled_data = scaler.fit_transform(data)
#concatenated_df['풋살인구합계'] = scaled_data

# 서울 생활인구 데이터 (평균) folium 설정

linear = cmp.LinearColormap(
        ['yellow', 'orange', 'red'],
        vmin=min(concatenated_df['풋살인구합계']), vmax=max(concatenated_df['풋살인구합계']),
        caption='시간대별 평균 풋살인구'
        )

living_population_2 = folium.Choropleth(geo_data=seoul_geo,
                            data=concatenated_df,
                            columns=['행정동명', '풋살인구합계'],
                            key_on='feature.properties.adm_nm',
                            fill_color='YlOrRd',
                            fill_opacity=0.7,
                            line_opacity=0.3,
                            overlay=False,
                            show=True,
                            legend_name='생활인구수',
                            highlight=True
                            ).geojson.add_to(f3)  # fg 변수에 추가

linear.add_to(seoul_map)
living_population_2.zoom_on_click = False
living_population_2.add_child(folium.features.GeoJsonTooltip(['adm_nm'], labels=False))

# -------------------------------------------------------------------------------------

# 서울 인구밀도 데이터 Streamlit 설정

st.sidebar.title("서울 인구밀도 데이터")
dense_check = st.sidebar.checkbox('인구밀도 표시', value=False)

# 서울 인구밀도 데이터 전처리

dense = pd.read_csv('인구밀도야.csv', encoding='utf-8')
dense = dense[['행정동명', '인구밀도']]

dense['인구밀도'] = scaler.fit_transform(dense[['인구밀도']])

# 서울 인구밀도 데이터 folium 설정

if dense_check:
    f2 = folium.FeatureGroup(name='인구밀도 데이터')
    seoul_map.add_child(f2)
    
    linear = cmp.LinearColormap(
        ['yellow', 'green', 'blue'],
        vmin=min(dense['인구밀도']), vmax=max(dense['인구밀도']),
        caption='인구밀도'
        )

    population_density = folium.Choropleth(geo_data = seoul_geo,
                        data = dense,
                        columns = ['행정동명', '인구밀도'],
                        key_on = 'feature.properties.adm_nm',
                        fill_color = 'YlGnBu',
                        fill_opacity = 0.7,
                        line_opacity = 0.3,
                        overlay = False,
                        legend_name = '인구밀집도',
                        highlight=True
                        ).geojson.add_to(f2)
                        
    linear.add_to(seoul_map)
    population_density.zoom_on_click = False
    population_density.add_child(folium.features.GeoJsonTooltip(['adm_nm'], labels=False))

# -------------------------------------------------------------------------------------

# 서울 주차장 데이터 Streamlit 설정

st.sidebar.title("서울 주차장 데이터")
parking_check = st.sidebar.checkbox('주차장 표시', value=False)

# 서울 주차장 데이터 전처리

parking = pd.read_csv('서울시 공영주차장.csv',encoding='euc-kr')

# 서울 주차장 데이터 folium 설정

if parking_check:
    m1 = folium.FeatureGroup(name='주차장 데이터')
    seoul_map.add_child(m1)

    for i in range(len(parking)):
        lat = parking.loc[i,'위도']
        long = parking.loc[i,'경도']
        name = parking.loc[i,'주차장명']
        folium.Circle(
                    [lat, long],
                    radius = 10,
                    color = 'red',
                    tooltip = name
                    ).add_to(m1)

# -------------------------------------------------------------------------------------

# 서울 지하철 승하차 데이터 Streamlit 설정

st.title("Seoul Map Data")
if st.button('새로고침'):
    st.experimental_rerun()

st.sidebar.title("서울 지하철 승하차 데이터")

sel_opt = ['승차','하차']
sel_box = st.sidebar.multiselect('승하차 여부를 선택하세요', sel_opt)

st.sidebar.header("시간대 조건")
col5, col6 = st.sidebar.columns(2)
with col5:
    start_time_sub = st.slider("시작시간", 0, 22, 0, 1, key=5)  # 0부터 22까지의 값을 선택할 수 있는 슬라이더

with col6:
    end_time_sub = st.slider("종료시간", 1, 23, 1, 1, key=6)  # 1부터 23까지의 값을 선택할 수 있는 슬라이더



# 서울 지하철 승차 데이터 전처리

df = pd.read_csv('지하철 승차.csv', encoding = 'utf-8') 
df = df.drop(columns = ['사용월', '호선명'], axis=1)

subway = pd.merge(df, js, how = 'inner', on = '지하철역')
g_subway = subway.groupby(['지하철역']).agg('mean')

lat = g_subway[['위도','경도']]
g_subway = g_subway.drop(columns = ['위도','경도'])

g_sub = pd.DataFrame(g_subway.stack())
g_sub = g_sub.rename(columns = {0 : '승차인원수'})

g_sub1 = pd.merge(g_sub,lat, how = 'left', on = '지하철역')

index = []
b = []
for i in g_sub.index:
    index.append(i[1])
for j in index:
    b.append(int(j[:2]))

g_sub1['시간대'] = b   
g_sub1 = g_sub1.dropna()

g_sub1['승하차여부'] = '승차'
g_sub1 = g_sub1.rename(columns={'승차인원수' : '인원수'})

# 서울 지하철 하차 데이터 전처리

df = pd.read_csv('지하철 하차.csv', encoding = 'utf-8') 
df = df.drop(columns = ['사용월', '호선명'], axis=1)

subway = pd.merge(df, js, how = 'inner', on = '지하철역')
g_subway = subway.groupby(['지하철역']).agg('mean')

lat = g_subway[['위도','경도']]
g_subway = g_subway.drop(columns = ['위도','경도'])

g_sub = pd.DataFrame(g_subway.stack())
g_sub = g_sub.rename(columns = {0 : '하차인원수'})

g_sub2 = pd.merge(g_sub,lat, how = 'left', on = '지하철역')

index = []
b = []
for i in g_sub.index:
    index.append(i[1])
for j in index:
    b.append(int(j[:2]))

g_sub2['시간대'] = b   
g_sub2 = g_sub2.dropna()

g_sub2['승하차여부'] = '하차'
g_sub2 = g_sub2.rename(columns = {'하차인원수' : '인원수'})

# 서울 지하철 승하차 folium 설정

if end_time > start_time:
    temp_sub1 = g_sub1[g_sub1['시간대'].between(start_time_sub, end_time_sub)]
    temp_sub2 = g_sub2[g_sub2['시간대'].between(start_time_sub, end_time_sub)]

m2 = folium.FeatureGroup(name='승차 데이터')
seoul_map.add_child(m2)

m3 = folium.FeatureGroup(name='하차 데이터')
seoul_map.add_child(m3)

for i in range(len(sel_box)):
    if sel_box[i] == '승차':
        for i in range(len(temp_sub1)):
            lat = temp_sub1.iloc[i,1]
            lng = temp_sub1.iloc[i,2]
            pop = temp_sub1.iloc[i,0]
            folium.CircleMarker([lat,lng],
                                radius = pop/5000,
                                color = 'green').add_to(m2)
    else:
        for i in range(len(temp_sub2)):
            lat = temp_sub2.iloc[i,1]
            lng = temp_sub2.iloc[i,2]
            pop = temp_sub2.iloc[i,0]
            folium.CircleMarker([lat,lng],
                                radius = pop/5000,
                                color = 'blue').add_to(m3)

# -------------------------------------------------------------------------------------

# 서울 풋살장 데이터 Streamlit 설정

st.sidebar.title('서울 풋살장 데이터')
sel_opt1 = ['민간', '공공']
sel_box1 = st.sidebar.multiselect('풋살장 종류를 골라주세요',sel_opt1)

# 서울 풋살장 데이터 전처리

public_futsal = pd.read_csv("서울공공1.csv")
public_futsal['info'] = public_futsal['구장명'] + " | " + public_futsal['비고']

private_futsal = pd.read_csv("서울민간1.csv")
private_futsal['info'] = private_futsal['구장명'] + " | " + private_futsal['비고'] + " | " + private_futsal['교육/대관']

# 서울 풋살장 데이터 folium 설정

m4 = folium.FeatureGroup(name='서울 공공 풋살장')
seoul_map.add_child(m4)

m5 = folium.FeatureGroup(name='서울 민간 풋살장')
seoul_map.add_child(m5)

for i in range(len(sel_box1)):
    if sel_box1[i] == '공공':
        for i in range(len(public_futsal)):
            lat = public_futsal.loc[i,'위도']
            long = public_futsal.loc[i,'경도']
            info = public_futsal.loc[i,'info']
    
            folium.Marker(
                    [lat, long],
                    icon=folium.Icon(icon ='ball', color = 'blue'),
                    tooltip = info
                    ).add_to(m4)
    else:
        for i in range(len(private_futsal)):
            lat = private_futsal.loc[i,'위도']
            long = private_futsal.loc[i,'경도']
            info = private_futsal.loc[i,'info']
    
            folium.Marker(
                    [lat, long],
                    icon=folium.Icon(icon ='ball', color = 'red'),
                    tooltip = info
                    ).add_to(m5)

# -----------------------------------folium load --------------------------------------------------------

folium.LayerControl().add_to(seoul_map)

st_folium(seoul_map, width=725)

# -----------------------------------지하철 barplot load --------------------------------------------------------

st.header('호선, 시간대 별 승/하차 인원수')
subway_range = st.radio('호선선택', options = ['1호선','2호선','3호선','4호선','5호선','6호선','7호선','8호선','9호선'])

df = pd.read_csv('지하철 승차.csv', encoding = 'utf-8') 
df = df.drop(columns = ['사용월'], axis=1)
df = df[df['호선명'] == subway_range]
g_subway3 = df.groupby(['호선명','지하철역']).agg('mean')
g_sub3 = pd.DataFrame(g_subway3.stack())
index = []
b= []
for i in g_sub3.index:
    index.append(i[2])

for j in index:
    b.append(int(j[:2]))

g_sub3['시간대'] = b   
g_sub3 = g_sub3.rename(columns = {0 : '승차 인원수'})
g_sub3 = g_sub3.dropna()

df = pd.read_csv('지하철 하차.csv', encoding = 'utf-8') 
df = df.drop(columns = ['사용월'], axis=1)
df = df[df['호선명'] == subway_range]

g_subway4 = df.groupby(['호선명','지하철역']).agg('mean')
g_sub4 = pd.DataFrame(g_subway4.stack())
index = []
b = []
for i in g_sub4.index:
    index.append(i[2])
for j in index:
    b.append(int(j[:2]))

g_sub4['시간대'] = b   
g_sub4 = g_sub4.rename(columns = {0 : '하차 인원수'})
g_sub4 = g_sub4.dropna()

if end_time > start_time:
    temp_sub3 = g_sub3[g_sub3['시간대'].between(start_time_sub, end_time_sub)]
    temp_sub4 = g_sub4[g_sub4['시간대'].between(start_time_sub, end_time_sub)]
c = []
for i in temp_sub3.index:
    c.append(i[1])
temp_sub3 = pd.DataFrame(index = c, data = temp_sub3['승차 인원수'].values, columns = ['승차 인원수'])
c = []
for i in temp_sub4.index:
    c.append(i[1])
temp_sub4 = pd.DataFrame(index = c, data = temp_sub4['하차 인원수'].values, columns = ['하차 인원수'])

st.write('승차 인원수 그래프 (사이드 바 시간과 연동)')
st.bar_chart(data = temp_sub3)
st.write('하차 인원수 그래프 (사이드 바 시간과 연동)')
st.bar_chart(data = temp_sub4)

# -----------------------------------생활인구 barplot load --------------------------------------------------------

st.header('지역/시간대별 평균 생활인구 필터링')
my_df = concatenated_df.copy()
my_df['행정동명'] = my_df['행정동명'].str.replace('서울특별시', '').str.strip()
sel_opt = my_df['행정동명']
sel_box = st.multiselect('지역을 선택하세요', sel_opt, default=('종로구 사직동', '강남구 논현1동', '은평구 진관동'))

my_df = my_df[my_df.행정동명.isin(sel_box)]
fig = plt.figure(figsize=(15,10))
ax = sns.barplot(x=my_df.행정동명, y=my_df.풋살인구합계, data=my_df)
ax.bar_label(ax.containers[0], label_type='center', color='white')
st.write('생활인구수 그래프 (사이드 바 시간과 연동)')
st.bar_chart(my_df, x='행정동명', y='풋살인구합계')