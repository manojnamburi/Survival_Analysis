"""
Author: Taesun Kim
Date:   1/15/2019

Title: Clean Retention Activity Data

Purpose:
    1. Explore Retention Activity Data.
    2. Make the Data Ready for Following Analyses.

Input: 
    1. "East Retention Activity Jan'17 through Dec'18.csv"
    2. "Churn_HH_Status.csv"

Output: 
    1. 'data_retention.pickle'

References:
    '00. Clean Data_v1.3.py'
"""


### 0. Import Required Packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pickle





### 1. Load Raw Data
## Offer/Discount Data
df_offer = pd.read_csv("East Retention Activity Jan'17 through Dec'18.csv")
df_offer.info()
df_offer.dtypes.value_counts()
df_offer.describe()

# Exclude Customers if Frequency >= 20
df_count_chc = df_offer['chc'].value_counts().to_frame().reset_index()
df_count_chc.columns = ['chc', 'chc_count']
df_count_chc['flag_chc_count'] = df_count_chc['chc_count'].apply(lambda x: True if x < 20 else False)

df_offer_flag = pd.merge(df_offer, df_count_chc,
                how = 'inner',
                on = 'chc')


## Churn Status Data
df_churn = pd.read_csv("Churn_HH_Status.csv")
df_churn.info()
df_churn['status'].value_counts()
# tmp = df_churn.head(n = 100)

## Merge Data on Customer ID
data = pd.merge(df_churn, df_offer_flag, 
                how = 'right',
                left_on = 'household_id', right_on = 'chc')





### 2. Creat New Vairables
## Sample Selection Criteria
# 1. 'prev_product_bundle':
#     - Include: 'VIDEO/OOL/OV', 'VIDEO/OOL', 'OOL', 'OOL/OV', 'VIDEO' + 'VIDEO/OV'
#           VIDEO/OOL/OV              1689255
#           VIDEO/OOL                  318251
#           OOL                        257525
#           OOL/OV                      85495
#           VIDEO                       71372
#           VIDEO/OV                     2596
#
#     - Exclude: 'Not Assigned', 'OV', 'Product 10', 'VIDEO/OOL/OV/FREEWHEEL'
#           Not Assigned               139590
#           OV                            976
#           Product 10                    800
#           VIDEO/OOL/OV/FREEWHEEL          1
#
# 2. 'save_flag': Include only ['Y', 'N']
#           Y    2035632
#           N     495450
#           S      34779
# 
# 3. 'chc_count': Exclude Customers if Frequency >= 20

list_product = ['VIDEO/OOL/OV', 'VIDEO/OOL', 'OOL', 'OOL/OV', 'VIDEO', 'VIDEO/OV']
data['flag_product'] = data['prev_product_bundle'].apply(lambda x: True if x in list_product else False)
data['flag_save'] = data['save_flag'].apply(lambda x: True if x in ['Y', 'N'] else False)

# Combine ['VIDEO', 'VIDEO/OV'] as 'VIDEO'.
data['product_bundle'] = data['prev_product_bundle'].apply(lambda x: 'VIDEO' if x in ['VIDEO', 'VIDEO/OV'] else x)


# Create Time-Related Variables
# Call Center Contact Time in Month, Week, and Day
data['contact_time_in_month'] = pd.to_datetime(data['rpt_date']).dt.to_period('M').apply(lambda x: x.start_time)
data['contact_time_in_week']  = pd.to_datetime(data['rpt_date']).dt.to_period('W').apply(lambda x: x.start_time)
data['contact_time_in_day']   = pd.to_datetime(data['rpt_date']).dt.to_period('D').apply(lambda x: x.start_time)

# Churn Time in Month, Week, and Day
# If Customer = Active, Set Churn Date = 2019-01-31. Monthly Billing Cycle
data['date_adj'] = data['date'].apply(lambda x: "2019-01-31 00:00:00.000000" if pd.isnull(x) else x)
data['churn_time_in_month'] = pd.to_datetime(data['date_adj']).dt.to_period('M').apply(lambda x: x.start_time)
data['churn_time_in_week']  = pd.to_datetime(data['date_adj']).dt.to_period('W').apply(lambda x: x.start_time)
data['churn_time_in_day']   = pd.to_datetime(data['date_adj']).dt.to_period('D').apply(lambda x: x.start_time)

# Duration in Month, Week, and Day
data['duration_in_month'] = data['churn_time_in_month'].dt.to_period('M') - data['contact_time_in_month'].dt.to_period('M')
data['duration_in_week']  = data['churn_time_in_week'].dt.to_period('W') - data['contact_time_in_week'].dt.to_period('W')
data['duration_in_day']   = data['churn_time_in_day'].dt.to_period('D') - data['contact_time_in_day'].dt.to_period('D')





### 3. Save Raw Data in pickle
with open('data_retention.pickle', 'wb') as f:
    pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
#
#with open('data_retention.pickle', 'rb') as f:
#    data = pickle.load(f)


