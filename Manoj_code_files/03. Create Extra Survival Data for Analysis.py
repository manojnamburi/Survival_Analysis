"""
Author: Taesun Kim
Date:   2/3/2019

Title: Create Extra Survival Data for Callback Analysis

Purpose:
    1. Need to Create Extra Data Including (df0.contact_time_in_month >= '2018-10-01 00:00:00') 
    2. Account for (1) Churn Type, (2) Product Type, and (3) Market Type in the Analysis.

Input: 
    1. 'data_retention.pickle'

Output: 
    1. 'data_survival_extra.pickle'

References:    
    See "02. Create Survival Data for Analysis.py".
    
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
    
df = data.loc[data.flag_chc_count & data.flag_product & data.flag_save & (data['begin_revenue'] > 0)]
df['Erosion'] = df['net_revenue_change'] * (-1)
df['Erosion_Pct'] = 100 * df['Erosion'] / df['begin_revenue']





### 2. Filter Data wrt Scope of Analysis
## (0) Save Customers Only
filter0 = (df.save_flag == 'Y')
# df.save_flag.value_counts()
df0 = df.loc[filter0]

# Check Unique Customer IDs.
df0.chc.unique().size
#tmp = df0.chc.value_counts()


## (1) Study Period: Oct 2018 ~
# filter1 = (df.save_flag == 'Y') & (df.contact_time_in_month < '2018-10-01 00:00:00') 
filter1 = (df0.contact_time_in_month >= '2018-10-01 00:00:00') 
df1  = df0.loc[filter1]
df10 = df0.loc[~filter1]
len(df1) + len(df10)
# df0.contact_time_in_month.value_counts().sort_index()

# Check Unique Customer IDs.
df1.chc.unique().size
df10.chc.unique().size


## (2) Customer Type: Customers Using 
filter2 = (df1['prev_product_bundle'] == df1['curr_product_bundle']) &\
          (df1['prev_videotier'] == df1['curr_videotier']) &\
          (df1['prev_speedtier'] == df1['curr_speedtier'])

df2 = df1.loc[filter2]
df20 = df1.loc[~filter2]
len(df2) + len(df20)

# Check Unique Customer IDs.
df2.chc.unique().size
df20.chc.unique().size


## (3) Erosion: Non-Negative Erosion
filter3 = (df2['Erosion'] >= 0)          
df3 = df2.loc[filter3]
df30 = df2.loc[~filter3]
len(df3) + len(df30)

# Check Unique Customer IDs.
df3.chc.unique().size
df30.chc.unique().size


## (4) Churn Type: (1) Voluntary Churn vs (2) All Churn Types
filter4 = (df3.status.isin(['ACTIVE', 'VOLUNTARY', 'MOVE AND TRANSFER', 'NON-PAY'])) &\
          (df3['duration_in_month'] >= 0)
df4 = df3.loc[filter4]
df40 = df3.loc[~filter4]
#df4.status.value_counts()
#(df4['duration_in_month'] >= 0).value_counts()
len(df4) + len(df40)

# Check Unique Customer IDs.
df4.chc.unique().size
df40.chc.unique().size

df4.loc[df4['status'] == 'ACTIVE']['chc'].unique().size
df4.loc[df4['status'] == 'VOLUNTARY']['chc'].unique().size
df4.loc[df4['status'] == 'MOVE AND TRANSFER']['chc'].unique().size
df4.loc[df4['status'] == 'NON-PAY']['chc'].unique().size

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
with open('data_survival_extra.pickle', 'wb') as f:
    pickle.dump(df4, f, pickle.HIGHEST_PROTOCOL)