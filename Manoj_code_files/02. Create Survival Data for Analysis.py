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

## (1) Study Period: Jan 2017 – Sep 2018
filter1 = (df.save_flag == 'Y') & (df.contact_time_in_month < '2018-10-01 00:00:00') 
df1 = df.loc[filter1]
# df0.contact_time_in_month.value_counts().sort_index()


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


## (3) Erosion: Non-Negative Erosion
filter3 = (df.save_flag == 'Y') & (df.contact_time_in_month < '2018-10-01 00:00:00') &\
          (df['prev_product_bundle'] == df['curr_product_bundle']) &\
          (df['prev_videotier'] == df['curr_videotier']) &\
          (df['prev_speedtier'] == df['curr_speedtier']) &\
          (df['Erosion'] >= 0)
df3 = df.loc[filter3]


## (4) Churn Type: (1) Voluntary Churn vs (2) All Churn Types
#  Exclude 'Null' & 'OTHER' Status
# df3.status.value_counts()
# df3.status.isnull().sum()
# (df3.status.isin(['ACTIVE', 'VOLUNTARY', 'MOVE AND TRANSFER', 'NON-PAY'])).value_counts()
filter4 = (df3.status.isin(['ACTIVE', 'VOLUNTARY', 'MOVE AND TRANSFER', 'NON-PAY']))
df4 = df3.loc[filter4]
df4['churn_voluntary'] = df4.status.isin(['VOLUNTARY']).astype('int')
df4['churn_all']       = df4.status.isin(['VOLUNTARY', 'MOVE AND TRANSFER', 'NON-PAY']).astype('int')

# Check Data
#varlist = ['status', 'churn_voluntary', 'churn_all', 'date', 'rpt_date', 'duration_in_month']
#tmp     = df4[varlist]

df4['Erosion'] = np.abs(df4.Erosion)
df4['Erosion_Pct'] = np.abs(df4.Erosion_Pct)

# Create Price Discount Buckets
bin0 = [-0.001, 0]
bin1 = np.arange(2, 22, 2).tolist()
bin2 = np.arange(25, 80, 5).tolist()
bin3 = [float("inf")]
price_category1 = bin0 + bin1 + bin2 + bin3
df4['Erosion_bin1'] = pd.cut(df4['Erosion'], price_category1)

bin0 = [-0.001, 0]
bin1 = np.arange(5, 55, 5).tolist()
bin2 = np.arange(60, 90, 10).tolist()
bin3 = [float("inf")]
price_category2 = bin0 + bin1 + bin2 + bin3
df4['Erosion_bin2'] = pd.cut(df4['Erosion'], price_category2)

bin0 = [-0.001, 0]
bin1 = np.arange(2, 42, 2).tolist()
bin2 = [50, 80]
bin3 = [float("inf")]
price_category3 = bin0 + bin1 + bin2 + bin3
df4['Erosion_Pct_bin1'] = pd.cut(df4['Erosion_Pct'], price_category3)

bin0 = [-0.001, 0]
bin1 = np.arange(2, 32, 2).tolist()
bin2 = [35, 40]
bin3 = [float("inf")]
price_category4 = bin0 + bin1 + bin2 + bin3
df4['Erosion_Pct_bin2'] = pd.cut(df4['Erosion_Pct'], price_category4)





## 3. Save Cleaned Survival Data in pickle
with open('data_survival.pickle', 'wb') as f:
    pickle.dump(df4, f, pickle.HIGHEST_PROTOCOL)