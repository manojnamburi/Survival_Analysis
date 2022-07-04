"""
Author: Taesun Kim
Date:   1/23/2019

Title: Modeling Survival Rate

Purpose:
    1. Examine the Impact of ARPU Erosion on Survival Rate.
    2. Account for (1) Churn Type, (2) Product Type, and (3) Market Type in the Analysis.

Input: 
    1. 'data_retention.pickle'

Output: 
    1. 'data_survival.pickle'

References:
    '02. Model Survival Rate.py'
"""


### 0. Import Required Packages
import pandas as pd
import numpy as np
import datetime as dt
import pickle
import matplotlib.pyplot as plt
#%matplotlib inline
import seaborn as sns
#import lifelines




#### 1. Load Data
### Use pickled data
import pickle
with open('data_retention.pickle', 'rb') as f:
    data = pickle.load(f)
    
## Sample Selection Criteria
# 1. 'prev_product_bundle':
#     - Include: 'VIDEO/OOL/OV', 'VIDEO/OOL', 'OOL', 'OOL/OV', 'VIDEO' + 'VIDEO/OV'
#     - Exclude: 'Not Assigned', 'OV', 'Product 10', 'VIDEO/OOL/OV/FREEWHEEL'
#
# 2. 'save_flag': Include only ['Y', 'N']
#           Y    2035632
#           N     495450
#           S      34779
# 
# 3. 'chc_count': Exclude Customers if Frequency >= 20
# 
# 4. 'cbegin_revenue': Exclude Customers if 'begin_revenue' <= 0
    
df = data.loc[data.flag_chc_count & data.flag_product & data.flag_save & (data['begin_revenue'] > 0)]
df['Erosion'] = df['net_revenue_change'] * (-1)
df['Erosion_Pct'] = 100 * df['Erosion'] / df['begin_revenue']





### 2. Filter Data wrt Scope of Analysis
## (0) Save Customers Only
filter0 = (df.save_flag == 'Y')
# df.save_flag.value_counts()
df0 = df.loc[filter0]
print('Study Period:               Jan 2017 - Dec 2018')
print(f'Number of Observation:      {df0.shape[0]}')
print(f'Number of Unique Customers: {df0.chc.nunique()}')


## (1) Study Period: Jan 2017 – Sep 2018
filter1 = (df.save_flag == 'Y') & (df.contact_time_in_month < '2018-10-01 00:00:00') 
df1 = df.loc[filter1]

df1['Flag_CustomerType'] = np.where((df1['prev_product_bundle'] == df1['curr_product_bundle']) &\
                                    (df1['prev_videotier'] == df1['curr_videotier']) &\
                                    (df1['prev_speedtier'] == df1['curr_speedtier']), 'homo', 'hetero')

s0 = df1.sort_values(['chc', 'contact_time_in_day']).\
     groupby(['chc']).agg({'Flag_CustomerType': ['first'],
                           'contact_time_in_day': ['count', min, max]})
s0.columns = ['Customer_Type', 'P_Count', 'P_Date_first', 'P_Date_last']

count_customers         = s0.Customer_Type.value_counts().to_frame().reset_index()
count_customers.columns = ['Customer_Type', 'Count_Customers']
count_calls             = s0.groupby('Customer_Type')['P_Count'].sum().to_frame().reset_index()
count_calls.columns     = ['Customer_Type', 'Count_Calls']
count_all               = pd.merge(count_customers, count_calls, on='Customer_Type')

print('Study Period:               Jan 2017 - Sep 2018')
print(f'Number of Observation:      {df1.shape[0]}')
print(f'Number of Unique Customers: {df1.chc.nunique()}')
print('Number of Customers and Calls by Customer Type')
print(count_all)

## (2) Customer Type: Customers Using 
##     the Same Product/Service before/after the Call
# Homogeneous Customers with Positive Erosion
filter2 = (df.save_flag == 'Y') & (df.contact_time_in_month < '2018-10-01 00:00:00') &\
          (df['prev_product_bundle'] == df['curr_product_bundle']) &\
          (df['prev_videotier'] == df['curr_videotier']) &\
          (df['prev_speedtier'] == df['curr_speedtier'])
df2 = df.loc[filter2]
# df2.prev_product_bundle.value_counts()
# df2.curr_product_bundle.value_counts()
# (df2['Erosion'] >= 0).value_counts()
# (df2['Erosion'] == 0).value_counts()































