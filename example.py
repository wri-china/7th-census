import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Load shapefile from AWS
shp = gpd.read_file('https://china-data-team-bucket-public.s3.cn-northwest-1.amazonaws.com.cn/7th_census/SHP_POP/China_POP_province.shp')
# Load population data from AWS
data = pd.read_excel('https://china-data-team-bucket-public.s3.cn-northwest-1.amazonaws.com.cn/7th_census/%E7%AC%AC%E4%B8%83%E6%AC%A1%E4%BA%BA%E5%8F%A3%E6%99%AE%E6%9F%A5%E5%88%86%E5%8E%BF%E6%95%B0%E6%8D%AE.xlsx', sheet_name='data_province')
# Merge shapefile and population data
merged_data = shp.merge(data, on='ID')
# Load boundary from AWS
nine_line_dash = gpd.read_file('https://china-data-team-bucket-public.s3.cn-northwest-1.amazonaws.com.cn/China_shapefile/%E4%B9%9D%E6%AE%B5%E7%BA%BF/%E4%B9%9D%E6%AE%B5%E7%BA%BF.shp')
boundary = gpd.read_file('https://china-data-team-bucket-public.s3.cn-northwest-1.amazonaws.com.cn/China_shapefile/%E5%9B%BD%E7%95%8C/%E5%9B%BD%E5%AE%B6%E7%9F%A2%E9%87%8F.shp')


##### Attribute calculation
result_df = data[['ID', '省', 'population_1', 'population_5']]
# Calculate minority population for provinces
result_df['minority_pop'] = (result_df['population_1'] * result_df['population_5'] / 100).round(0).astype(int)
# Rename columns
result_df = result_df.rename(columns={'population_1': 'total_pop',
                                      'population_5': 'minority_pct'})
# Sort by minority population
result_df = result_df.sort_values(by='minority_pop', ascending=False)
print(result_df)


##### Plotting
# Map
fig, ax = plt.subplots(figsize=(12, 10))  # Adjust the size as needed
# Plotting boundary
nine_line_dash.plot(ax=ax,
                    edgecolor='grey')
boundary.plot(ax=ax,
              edgecolor='grey',
              facecolor='grey')
# Plotting data
merged_data.plot(ax=ax,
                 column='population_1',
                 cmap='inferno_r',
                 edgecolor='grey',
                 legend=True,
                 legend_kwds={'shrink': 0.6})
# Adding titles and labels
ax.set_title("Total population by province", fontsize=18)
# Adjust layout
plt.tight_layout()
# Show the chart
plt.show()

# Pie chart
provinces = ['Beijing', 'Shanghai', 'Henan', 'Xizang']
# Create subplots
fig, axs = plt.subplots(2, 2, figsize=(15, 15))  # Adjust the size as needed
axs = axs.ravel()
for i, province in enumerate(provinces):
    province_data = merged_data[merged_data['ENG_NAME'] == province]
    axs[i].pie(province_data[['age_39', 'age_40', 'age_41']].values.flatten(),
               labels=['Age 0-14', 'Age 15-64', 'Age 65+'],
               autopct='%1.1f%%',
               colors=['#90F1EF', '#FFD6E0', '#FFEF9F'])
    axs[i].set_title(f"Population age distribution of {province}", fontsize=16)
# Adjust layout
plt.tight_layout()
# Show the chart
plt.show()

# Bar chart
# Select and sort the data
finance_data = merged_data.dropna(subset=['job_21', 'ENG_NAME'])
sorted_pairs = sorted(zip(finance_data[['job_21']].values.flatten(), finance_data[['ENG_NAME']].values.flatten()))
sorted_values, sorted_labels = zip(*sorted_pairs)
# Create the bar chart
fig, ax = plt.subplots(figsize=(10, 8))
plt.barh(sorted_labels, 
         sorted_values, 
         color=plt.cm.Blues(np.linspace(0.1, 1, len(sorted_values))))
# Adding titles and labels
plt.xlabel('No. of People in Finance', fontsize=14)
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')
# Adjust layout
plt.tight_layout()
# Show the chart
plt.show()
