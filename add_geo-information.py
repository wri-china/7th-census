# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 15:29:06 2023

@author: Yuchen.Guo
"""

import requests
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import os

def geocode_address(address_list, api_key):
    
    LON = []
    LAT = []
    Full_name = []

    for nn,query in enumerate(address_list):
        url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}'.format(query.strip(), api_key)
        response = requests.get(url)
        outpp = response.json()['results'][0]['address_components']

    
        
        full_name = ''
        for op in outpp:
           
            full_name = full_name + op['long_name'] + ','
            
        Full_name.append(full_name[:-1]) 
        lat = response.json()['results'][0]['geometry']['location']['lat']
        lng = response.json()['results'][0]['geometry']['location']['lng']
        LON.append(lng)
        LAT.append(lat)

    return LON, LAT, Full_name


with open('C:/Users/Yuchen.Guo/OneDrive/WRI/project/BRI/key.txt') as f:
    f = f.readlines()
api_key = f[0]   
GOOGLE_MAPS_API_KEY = api_key


######省
shp_province = gpd.read_file('C:/Users/Yuchen.Guo/OneDrive/WRI/github/shpfile/2020年_CTAmap_1.12版/2020年省级/2020年省级.shp')
shp_province.set_index('省',inplace = True)
province = pd.read_excel('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/第七次人口普查分县数据_1128.xlsx',sheet_name = 'new_data_province' )
province.set_index('ID',inplace = True)
shp_province_new = shp_province.reindex(province['省'])
shp_province_new['ID'] = province.index 
shp_province_new.reset_index().dropna(subset=['geometry']).to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_province.shp', index = False,driver='ESRI Shapefile',encoding='utf-8')


a = province.index.values
b= shp_province_new.reset_index().dropna(subset=['geometry'])['ID'].values
empty = set(a) - set(b)

######市
shp_city = gpd.read_file('C:/Users/Yuchen.Guo/OneDrive/WRI/github/shpfile/2020年_CTAmap_1.12版/2020年地级/2020年地级.shp')
shp_city['all_name'] = shp_city['省级'] + shp_city['地名']
shp_city.set_index('all_name',inplace = True)

city = pd.read_excel('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/第七次人口普查分县数据_1128.xlsx',sheet_name = 'new_data_city' )
city.set_index('ID',inplace = True)
city['all_name'] = city['省']+city['市']


shp_city_new = shp_city.reindex(city['all_name'])
shp_city_new['ID'] = city.index 
shp_city_new.reset_index().dropna(subset=['geometry']).to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_city.shp', index = False,driver='ESRI Shapefile',encoding='utf-8')

a = city.index.values
b= shp_city_new.reset_index().dropna(subset=['geometry'])['ID'].values
empty = set(a) - set(b)


######县

shp_county = gpd.read_file('C:/Users/Yuchen.Guo/OneDrive/WRI/github/shpfile/2020年_CTAmap_1.12版/2020年县级/2020年县级.shp')
shp_county['all_name'] = shp_county['省级'] +shp_county['地级']+ shp_county['地名']
shp_county.set_index('all_name',inplace = True)


county = pd.read_excel('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/第七次人口普查分县数据_1128.xlsx',sheet_name = 'new_data_county' )
county.set_index('ID',inplace = True)
county['all_name'] = county['省']+county['市']+county['县']

shp_county_new = shp_county.reindex(county['all_name'])
shp_county_new['ID'] = county.index 
shp_county_new.reset_index().dropna(subset=['geometry']).to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county.shp', index = False,driver='ESRI Shapefile',encoding='utf-8')

a = county.index.values
b = shp_county_new.reset_index().dropna(subset=['geometry'])['ID'].values
empty = set(a) - set(b)



address_list = county.loc[list(empty)]['all_name']

exists =  os.path.exists('C:/Users/Yuchen.Guo/OneDrive/WRI/github/shpfile/datamissingname.csv')

if exists:
    
    datamissingname = pd.read_csv('C:/Users/Yuchen.Guo/OneDrive/WRI/github/shpfile/datamissingname.csv').set_index('ID')

else:
    LON, LAT, Full_name = geocode_address(address_list, api_key)

    datamissingname = pd.DataFrame({'lon':LON,'lat':LAT,'Full_name':Full_name,'all_name':address_list,'ID':address_list.index}).set_index('ID')
    
    datamissingname.to_csv('C:/Users/Yuchen.Guo/OneDrive/WRI/github/shpfile/datamissingname.csv')

points = [Point(lon,lat)for lon,lat in zip(datamissingname['lon'],datamissingname['lat'])]


datamissing = pd.DataFrame()

for pp,idd in zip(points,address_list.index):
    
    dd = shp_county[shp_county.contains(pp)].reset_index().rename(index = {0:idd})
    
    datamissing  = pd.concat([datamissing,dd])

datamissing.drop(columns=['all_name'], inplace=True)

datamissing = pd.merge(datamissingname, datamissing, left_index=True, right_index=True)

gdf = datamissing.reset_index().dropna(subset=['geometry']).rename(columns = {'index':'ID'})
gpd.GeoDataFrame(gdf, geometry='geometry').to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county_need_further_clean.shp',driver='ESRI Shapefile',encoding='utf-8')


China_county = gpd.read_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county.shp').set_index('ID')

China_county_need_further_clean = gpd.read_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county_need_further_clean.shp').set_index('ID')

CN = set(China_county_need_further_clean['区划码'].values)
CC = set(China_county['区划码'].values)

iiid = CN - (CN & CC)
xiid = CN & CC

xiID = [China_county_need_further_clean[China_county_need_further_clean['区划码'] == ii].index[0] for ii in xiid]


uiID = [China_county_need_further_clean[China_county_need_further_clean['区划码'] == ii].index[0] for ii in iiid]


China_county_ = China_county_need_further_clean.loc[uiID][China_county.columns[:]]


China_county_need_further_clean.loc[xiID][China_county.columns[:]]

China_county_final = pd.concat([China_county,China_county_])

China_county_final.reset_index().to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county_v2.shp',index = False,driver='ESRI Shapefile',encoding='utf-8')



emp = set(shp_county['区划码'].values)-set(China_county_final['区划码'].values)

noboundry_cen  = set(county.index) -  set(China_county_final.index)

Dataframe = pd.DataFrame()

for province, dataframex in county.loc[list(noboundry_cen)].sort_values(by='省', ascending=False).groupby('省'):
    
    for ID, vv in dataframex.iterrows():
        print(vv.all_name)
        
        county_vv_x = shp_county[(shp_county['省级'] ==province)]['地名'].index[0]
        
        contains_string = '不统计' in county_vv_x
        
        if contains_string:
            
            county_vv = shp_county[(shp_county['省级'] ==province)]['地名']
            
            #county_vv.index = county_vv.index.astype(str).str.replace('不统计', '')
        
        else:
            
            county_vv= shp_county[(shp_county['省级'] ==province)&(shp_county['地级'] ==vv['市'])]['地名']
        
        text_county = county_vv.keys().tolist()#.to_json().encode('utf-8').decode('unicode_escape')#','.join(list(county_vv.index))
        
        text_vv = ''.join(vv[['省', '市', '县']].values)
        
        result = f' text_vv:{text_vv} 和 text_county:{text_county} '
        
        print(result)
        name = input()
        dataframe = pd.DataFrame([{'status':name}])
        dataframe = dataframe.rename({0:ID})
        Dataframe = pd.concat([Dataframe,dataframe])
        
        
data = {
    "ID": [838, 833, 830, 22, 2334],
    "Description": [
        "上海市不统计金山区",
        "上海市不统计杨浦区",
        "上海市不统计静安区",
        "天津市不统计河西区",
        "海南省三沙市南沙区"
    ]
}

# Create a DataFrame
df = pd.DataFrame(data)

shp_cty = shp_county.loc[df['Description']].reset_index()[China_county.columns[:]]
shp_cty['ID'] = df['Description'].index
#shp_cty = #shp_county.loc[[838, 833, 830, 22, 2334]]
shp_cty.set_index('ID').reset_index().to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county_v2_added.shp',index = False,driver='ESRI Shapefile',encoding='utf-8')

ddd = Dataframe[Dataframe['status'] != 'None'].drop(index = 873)

dddd = Dataframe[Dataframe['status'] != 'None'].dropna()


shp_cty = shp_county.loc[ddd['status']].reset_index()[China_county.columns[:]]
shp_cty['ID'] = ddd['status'].index



final_shapefile = pd.concat([shp_cty.set_index('ID'),China_county_final])


 

empty_shapefile = shp_county.set_index('区划码').loc[list(set(shp_county['区划码'])-set(final_shapefile['区划码']))]


es = empty_shapefile.loc[['310109']].reset_index()

es['all_name'] = final_shapefile.loc[[832]]['all_name'].values[0]


final_shapefile.loc[[832]] = es[final_shapefile.columns].values

final_shapefile.reset_index().to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county_v3.shp',index = False,driver='ESRI Shapefile',encoding='utf-8')

for iiddd, value in empty_shapefile[:].iterrows():
    print(value['省级'],value['地级'],value['地名']) 
    p_county = county[county['省'] == value['省级']]
    p_county[p_county['市'] == value['地级']]
    
    
    
need_v_shape = shp_county.set_index('区划码').loc[np.array(county[county['年份'] == 'F2020'].index).astype(str)]

need_v_shape['ID'] = need_v_shape.index

county[county['年份'] == 'F2020']['all_name']

need_v_shape['all_name'] = county[county['年份'] == 'F2020']['all_name'].values
    
need_v_shape_ = need_v_shape.reset_index().set_index('ID')[final_shapefile.columns]

final_shapefile_ = pd.concat([need_v_shape_,final_shapefile])

final_shapefile_.reset_index().to_file('C:/Users/Yuchen.Guo/OneDrive - World Resources Institute/RDI/Data Team/7th CENSUS/China_county_v3.shp',index = False,driver='ESRI Shapefile',encoding='utf-8')


    
    
    
    
    
    
    
    