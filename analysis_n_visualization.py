import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load shapefile
shp = gpd.read_file('https://china-data-team-bucket-public.s3.cn-northwest-1.amazonaws.com.cn/7th_census/SHP_POP/China_POP_province.shp')
# Load population data
data = pd.read_excel('https://china-data-team-bucket-public.s3.cn-northwest-1.amazonaws.com.cn/7th_census/%E7%AC%AC%E4%B8%83%E6%AC%A1%E4%BA%BA%E5%8F%A3%E6%99%AE%E6%9F%A5%E5%88%86%E5%8E%BF%E6%95%B0%E6%8D%AE.xlsx', sheet_name='data_province')
# Merge shapefile and population data
merged_data = shp.merge(data, on='ID')


# Plotting
# Map
fig, ax = plt.subplots(figsize=(10, 10))  # Adjust the size as needed
merged_data.plot(ax=ax, 
                 column='population_1', 
                 cmap='Oranges', 
                 edgecolor='grey',
                 legend=True)
# Adding titles and labels
ax.set_title("Population by province")
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
               autopct='%1.1f%%')
    axs[i].set_title(f"Population age distribution of {province}")
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
fig, ax = plt.subplots(figsize=(10, 15)) 
plt.barh(sorted_labels, sorted_values)
# Adding titles and labels
plt.xlabel('No. of People in Finance')
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top')
# Show the chart
plt.show()
