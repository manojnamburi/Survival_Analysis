"""
Author: Taesun Kim
Date:   2/4/2019

Title: Explore Number of Callbacks after Receiving Positive Erosions

Purpose:
    1. Summarize Callbacks wrt Erosion Percentage
    2. Compre Callbacks by Group

Input: 
    1. 'data_survival.pickle'
    2. 'data_survival_extra.pickle'

Output: 

References:    
    1. "02. Create Survival Data for Analysis".
    2. "03. Create Extra Survival Data for Analysis".

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





### 1. Impoart Primary Survival Data
#import pickle
with open('data_survival.pickle', 'rb') as f:
    data_survival = pickle.load(f)

# For Some REASONS, 'duration' is saved in string. Convert it to interger.
data_survival['duration_in_month'] = data_survival['duration_in_month'].astype('int')
data_survival['duration_in_week']  = data_survival['duration_in_week'].astype('int')
data_survival['duration_in_day']   = data_survival['duration_in_day'].astype('int')

data_survival['Erosion_Int']   = data_survival['Erosion'].round().astype('int')
data_survival['Erosion_Pct_Int']   = data_survival['Erosion_Pct'].round().astype('int')


# a. Remove Duplicated Records
# Note that df.drop_duplicates(keep = False) exclude all duplicates.
data = data_survival.copy()    
data = data.drop_duplicates()
data.Erosion.describe()


# b. Find the 1st Positive Erosion Date
#df['Erosion_Pct'] = df['Erosion'] / df['begin_revenue']
import datetime as dt
from dateutil.relativedelta import relativedelta

s0 = data.loc[(data['Erosion'] > 0)].sort_values(['chc', 'contact_time_in_day']).\
     groupby(['chc']).agg({'contact_time_in_day': ['count', min, max],
            'Erosion': ['first', 'last', 'sum'],
            'begin_revenue': ['first']})

# Rename 'begin_revenue' as 'save_revenue'.    
s0.columns = ['P_Count', 'P_Date_first', 'P_Date_last', 'P_Money1', 'P_Money2', 'P_Money_Sum', 'save_revenue']
s0['chc'] = s0.index
s0 = s0.sort_values('P_Count', ascending = False)
s0['Offer_Int'] = round(100 * s0.P_Money1/s0.save_revenue).astype('int')

# Check Data
# tmp = data.loc[data.chc == 785893098902].sort_values('contact_time_in_day')


s0['P_Date_3mon']  = pd.to_datetime(s0.P_Date_first.dt.date + relativedelta(months = +3))
s0['P_Date_6mon']  = pd.to_datetime(s0.P_Date_first.dt.date + relativedelta(months = +6))
s0['P_Date_9mon']  = pd.to_datetime(s0.P_Date_first.dt.date + relativedelta(months = +9))
s0['P_Date_12mon'] = pd.to_datetime(s0.P_Date_first.dt.date + relativedelta(months = +12))
s0['Date_cutoff']  = pd.to_datetime('2019-01-01 00:00:00')

#s0 = s0.drop(['begin_revenue'], axis=1)

#pd.concat([s0.P_Count.value_counts(), s0.P_Count.value_counts()/len(s0)], axis=1)
#   P_Count   P_Count_Pct
#1   280178  0.844286       ---> 0 Call after Receiving 1st Positive Offer
#2    42189  0.127132
#3     7450  0.022450
#4     1563  0.004710
#5      368  0.001109
#6       79  0.000238
#7       18  0.000054
#8        5  0.000015
#9        2  0.000006





### 2. Get Extra Data and Combine with the Primary Data
#import pickle
with open('data_survival_extra.pickle', 'rb') as f:
    data_extra = pickle.load(f)

# For Some REASONS, 'duration' is saved in string. Convert it to interger.
data_extra['duration_in_month'] = data_extra['duration_in_month'].astype('int')
data_extra['duration_in_week']  = data_extra['duration_in_week'].astype('int')
data_extra['duration_in_day']   = data_extra['duration_in_day'].astype('int')

data_extra['Erosion_Int']   = data_extra['Erosion'].round().astype('int')
data_extra['Erosion_Pct_Int']   = data_extra['Erosion_Pct'].round().astype('int')

data_extra = data_extra.drop_duplicates()
data_extra.Erosion.describe()

# Combine (1) Survival Data and (2) Extra Data
data_all = pd.concat([data, data_extra], axis=0)
data_all['Call_count'] = 1
data_all['Call_positive'] = (data_all['Erosion'] > 0).astype('int')





### 3. Create Data for Callback Analysis
df = pd.merge(s0, data_all, left_on = 'chc', right_on = 'chc', how = 'inner')


# Set Call, Offer, & Erosion = 0 on the 1st Postive Erosion Date
df['Call_count_0'] = df.Call_count
df.loc[(df.contact_time_in_day == df.P_Date_first), ['Call_count_0']] = 0

df['Call_positive_0'] = df.Call_positive
df.loc[(df.contact_time_in_day == df.P_Date_first), ['Call_positive_0']] = 0

df['Erosion_0'] = df.Erosion
df.loc[(df.contact_time_in_day == df.P_Date_first), ['Erosion_0']] = 0

df.columns
var_list = ['chc', 'P_Date_first', 'rpt_date', 'begin_revenue', 'end_revenue', 'net_revenue_change', \
            'Offer_Int', 'Erosion_0', 'Call_count', 'Call_count_0', 'Call_positive', 'Call_positive_0',]
tmp = df[var_list]



#df = df.sort_values(['P_Count', 'chc', 'contact_time_in_day'])

# No Duplicates: Some Records Are Slightly Different.
# Use This for Analysis
df_nd = df.drop_duplicates(['chc', 'rpt_date', 'begin_revenue', 'end_revenue', 'net_revenue_change'])


# 1st Positve Offers: Offer_Int in [ 5, 7, 10, 12, 15, 17,  20]
# All Calls over 1/2017-12/2018
df1 = df_nd.query('contact_time_in_day >= P_Date_first &\
             Offer_Int in [ 5, 7, 10, 12, 15, 17,  20]')

# Trailing 12 Month Calls after the 1st Positive Offer
df2 = df_nd.query('contact_time_in_day >= P_Date_first &\
             contact_time_in_day <= P_Date_12mon &\
             P_Date_12mon < Date_cutoff &\
             Offer_Int in [ 5, 7, 10, 12, 15, 17,  20]')
#(df2.contact_time_in_day <= df2.P_Date_12mon).value_counts()
#(df2.P_Date_12mon <= df2.Date_cutoff).value_counts()
# df2.contact_time_in_day.describe()

# Trailing 9 Month Calls after the 1st Positive Offer
df3 = df_nd.query('contact_time_in_day >= P_Date_first &\
             contact_time_in_day <= P_Date_9mon &\
             P_Date_9mon < Date_cutoff &\
             Offer_Int in [ 5, 7, 10, 12, 15, 17,  20]')
#(df3.contact_time_in_day <= df3.P_Date_9mon).value_counts()
#(df3.P_Date_9mon <= df3.Date_cutoff).value_counts()

# Trailing 6 Month Calls after the 1st Positive Offer
df4 = df_nd.query('contact_time_in_day >= P_Date_first &\
             contact_time_in_day <= P_Date_6mon &\
             P_Date_6mon < Date_cutoff &\
             Offer_Int in [ 5, 7, 10, 12, 15, 17,  20]')
#(df4.contact_time_in_day <= df4.P_Date_6mon).value_counts()
#(df4.P_Date_6mon <= df4.Date_cutoff).value_counts()

# Trailing 3 Month Calls after the 1st Positive Offer
df5 = df_nd.query('contact_time_in_day >= P_Date_first &\
             contact_time_in_day <= P_Date_3mon &\
             P_Date_3mon < Date_cutoff &\
             Offer_Int in [ 5, 7, 10, 12, 15, 17,  20]')
#(df5.contact_time_in_day <= df5.P_Date_3mon).value_counts()
#(df5.P_Date_3mon <= df5.Date_cutoff).value_counts()



# 12 Month Calls
dfi = df2 
s1 = dfi.groupby(['chc']).agg({'Offer_Int': ['first'],
               'Call_count_0':['sum'],
               'Call_positive_0': ['sum'],
               'Erosion_0': ['sum']})
#tmp = df2.loc[df2.chc == 780116083406, var_list]
s1.columns = ['First_Offer', 'Calls_Count', 'Offers_Count', 'Offers_Sum']
s1['Offers_Mean'] = (s1.Offers_Sum/s1.Calls_Count).fillna(0)
s1['chc'] = s1.index


s2 = s1.groupby(['First_Offer']).agg({'Calls_Count': ['count', 'sum', 'mean'],
               'Offers_Count':['sum', 'mean'],
               'Offers_Sum':['sum', ]})
s2.columns = ['First_Offer_Count', 'Total_Call_Count', 'Avg_Call_Count', 
              'Total_Offer_Count', 'Avg_Offer_Count', 'Total_Offer_Amt']
s2['Dollars_per_Call'] = s2.Total_Offer_Amt/s2.Total_Call_Count
s2['Dollars_per_Offer'] = s2.Total_Offer_Amt/s2.Total_Offer_Count
s2['First_Offer'] = s2.index
var_list = ['First_Offer'] + list(s2)[:-1]
s2 = s2[var_list]


# Callback Summary Table   
s2.to_csv('Callbacks.csv', index=False)


# Callback Frequency Table
pivot1 = pd.pivot_table(s1,
                        index   = 'First_Offer',
                        columns = 'Calls_Count',
                        values  = 'chc', 
                        aggfunc = 'count').fillna(0)
pivot1.to_csv('Callbacks_pivot_call.csv', index=True)

pivot2 = pd.pivot_table(s1,
                        index   = 'First_Offer',
                        columns = 'Offers_Count',
                        values  = 'chc', 
                        aggfunc = 'count').fillna(0)
pivot2.to_csv('Callbacks_pivot_offer.csv', index=True)





### 4. Do Additional Analysis: 12 Month Sales
## Compute Segment Pct
# Total Number of Unique chc
# dfi.chc.unique().size
# Out[14]: 156781

# Monthly Sales by 'chc'
sales = pd.read_csv('Retention_Sales.csv')
sales.info()
sales.household_id.unique().size
sales['month_sales'] = pd.to_datetime(sales['dt'].astype('str') + '01')
#tmp = sales.query('chc == 780100045701').sort_values('month_sales')
#tmp = sales.head(n=100)



# Append 12 month sales to each customer.
dfi = df_nd.query('contact_time_in_day >= P_Date_first &\
             contact_time_in_day <= P_Date_12mon &\
             P_Date_12mon < Date_cutoff')

s1 = dfi.groupby(['chc']).agg({'Offer_Int': ['first'],
               'Call_count_0':['sum'],
               'Call_positive_0': ['sum'],
               'Erosion_0': ['sum'],
               'save_revenue': ['first'],
               'status': ['first'],
               'churn_time_in_day': ['first'],
               'P_Date_first': ['first'],
               'P_Date_12mon': ['first']})

s1.columns = ['First_Offer', 'Calls_Count', 'Offers_Count', 'Offers_Sum', 'Save_Revenue', \
              'status', 'churn_time_in_day', 'P_Date_first',  'P_Date_12mon']
s1['chc'] = s1.index

# Convert 'P_Date_12mon_first' into the 1st day of that month.
# https://stackoverflow.com/questions/45304531/extracting-the-first-day-of-month-of-a-datetime-type-column-in-pandas
s1['P_Date_12mon_first'] = s1.P_Date_12mon.astype('datetime64[M]')

s2 = pd.merge(s1, sales, how='left', left_on=['chc', 'P_Date_12mon_first'], \
              right_on=['chc', 'month_sales'])

# Note 'status' doesn't exactly match 'revenue_m0'.
s2['status2'] = np.where((s2.churn_time_in_day >= s2.P_Date_12mon_first) &\
                         (s2.revenue_m0 > 0), 'ACTIVE', s2.status)
s2['Last_Revenue'] = np.where(s2.revenue_m0 <= 0, np.nan, s2.revenue_m0)

var_list = ['First_Offer', 'Calls_Count', 'Offers_Count', 'Offers_Sum', 'Save_Revenue', 'Last_Revenue']
s2[var_list].agg(['count', 'mean', 'sum']).to_csv('Callbacks.csv', index=True)
s2.status2.value_counts().to_csv('Callbacks_status.csv', index=True)
s2.First_Offer.value_counts().sort_index().to_csv('Callbacks_freq.csv', index=True)



## Things to Do by Erosion Segment
#1. Compute Total Begin Revenue by Seg
#2. Compute Month 12 Survival Rate by Seg
#3. Compute Total Calls within 12 Months by Seg
#4. Compute Total Offers within 12 Months by Seg
#5. Compute Month 12 Total Revenue by Seg
#   Need data from the Team

# 12 Month Calls
dfi = df2 
s1 = dfi.groupby(['chc']).agg({'Offer_Int': ['first'],
               'Call_count_0':['sum'],
               'Call_positive_0': ['sum'],
               'Erosion_0': ['sum'],
               'save_revenue': ['first'],
               'status': ['first'],
               'churn_time_in_day': ['first'],
               'P_Date_first': ['first'],
               'P_Date_12mon': ['first']})

s1.columns = ['First_Offer', 'Calls_Count', 'Offers_Count', 'Offers_Sum', 'Save_Revenue', \
              'status', 'churn_time_in_day', 'P_Date_first',  'P_Date_12mon']
s1['chc'] = s1.index

s1['P_Date_12mon_first'] = s1.P_Date_12mon.astype('datetime64[M]')

s2 = pd.merge(s1, sales, how='left', left_on=['chc', 'P_Date_12mon_first'], \
              right_on=['chc', 'month_sales'])

# Note 'status' doesn't exactly match 'revenue_m0'.
s2['status2'] = np.where((s2.churn_time_in_day >= s2.P_Date_12mon_first) &\
                         (s2.revenue_m0 > 0), 'ACTIVE', s2.status)
s2['Last_Revenue'] = np.where(s2.revenue_m0 <= 0, np.nan, s2.revenue_m0)


# Survival Rate in 12 Months
pivot1 = pd.pivot_table(s2,
                        index   = 'status2',
                        columns = 'First_Offer',
                        values  = 'chc', 
                        aggfunc = 'count').fillna(0)
pivot1.to_csv('Callbacks_status_seg.csv', index=True)



s3 = s2.groupby(['First_Offer']).agg({'Calls_Count': ['count', 'sum', 'mean'],
               'Offers_Count':['sum', 'mean'],
               'Offers_Sum':['sum', ],
               'Save_Revenue': ['count', 'sum', 'mean'],
               'Last_Revenue': ['count', 'sum', 'mean']})
s3.columns = ['First_Offer_Count', 'Total_Call_Count', 'Avg_Call_Count', 
              'Total_Offer_Count', 'Avg_Offer_Count', 'Total_Offer_Amt',
              'Save_Revenue_Count', 'Save_Revenue_Sum', 'Save_Revenue_Avg',
              'Last_Revenue_Count', 'Last_Revenue_Sum', 'Last_Revenue_Avg']
#s3['Dollars_per_Call'] = s3.Total_Offer_Amt/s3.Total_Call_Count
#s3['Dollars_per_Offer'] = s3.Total_Offer_Amt/s3.Total_Offer_Count
s3['First_Offer'] = s3.index
var_list = ['First_Offer'] + list(s3)[:-1]
s3 = s3[var_list]
s3.to_csv('Callbacks_seg.csv', index=True)





### 5. Do Additional Analysis: 6 Month Sales
## Compute Segment Pct
# Total Number of Unique chc
# dfi.chc.unique().size
# Out[14]: 156781

## Monthly Sales by 'chc'
#sales = pd.read_csv('Retention_Sales.csv')
#sales.info()
#sales.household_id.unique().size
#sales['month_sales'] = pd.to_datetime(sales['dt'].astype('str') + '01')
##tmp = sales.query('chc == 780100045701').sort_values('month_sales')
##tmp = sales.head(n=100)



# Append 6 Month sales to each customer.
dfi = df_nd.query('contact_time_in_day >= P_Date_first &\
             contact_time_in_day <= P_Date_6mon &\
             P_Date_6mon < Date_cutoff')

s1 = dfi.groupby(['chc']).agg({'Offer_Int': ['first'],
               'Call_count_0':['sum'],
               'Call_positive_0': ['sum'],
               'Erosion_0': ['sum'],
               'save_revenue': ['first'],
               'status': ['first'],
               'churn_time_in_day': ['first'],
               'P_Date_first': ['first'],
               'P_Date_6mon': ['first']})

s1.columns = ['First_Offer', 'Calls_Count', 'Offers_Count', 'Offers_Sum', 'Save_Revenue', \
              'status', 'churn_time_in_day', 'P_Date_first',  'P_Date_6mon']
s1['chc'] = s1.index

# Convert 'P_Date_6mon_first' into the 1st day of that month.
s1['P_Date_6mon_first'] = s1.P_Date_6mon.astype('datetime64[M]')

s2 = pd.merge(s1, sales, how='left', left_on=['chc', 'P_Date_6mon_first'], \
              right_on=['chc', 'month_sales'])

# Note 'status' doesn't exactly match 'revenue_m0'.
s2['status2'] = np.where((s2.churn_time_in_day >= s2.P_Date_6mon_first) &\
                         (s2.revenue_m0 > 0), 'ACTIVE', s2.status)
s2['Last_Revenue'] = np.where(s2.revenue_m0 <= 0, np.nan, s2.revenue_m0)

var_list = ['First_Offer', 'Calls_Count', 'Offers_Count', 'Offers_Sum', 'Save_Revenue', 'Last_Revenue']
s2[var_list].agg(['count', 'mean', 'sum']).to_csv('Callbacks.csv', index=True)
s2.status2.value_counts().to_csv('Callbacks_status.csv', index=True)
s2.First_Offer.value_counts().sort_index().to_csv('Callbacks_freq.csv', index=True)



## Things to Do by Erosion Segment
#1. Compute Total Begin Revenue by Seg
#2. Compute Month 6 Survival Rate by Seg
#3. Compute Total Calls within 6 Months by Seg
#4. Compute Total Offers within 6 Months by Seg
#5. Compute Month 6 Total Revenue by Seg
#   Need data from the Team

# 6 Month Calls
dfi = df4 
s1 = dfi.groupby(['chc']).agg({'Offer_Int': ['first'],
               'Call_count_0':['sum'],
               'Call_positive_0': ['sum'],
               'Erosion_0': ['sum'],
               'save_revenue': ['first'],
               'status': ['first'],
               'churn_time_in_day': ['first'],
               'P_Date_first': ['first'],
               'P_Date_6mon': ['first']})

s1.columns = ['First_Offer', 'Calls_Count', 'Offers_Count', 'Offers_Sum', 'Save_Revenue', \
              'status', 'churn_time_in_day', 'P_Date_first',  'P_Date_6mon']
s1['chc'] = s1.index

s1['P_Date_6mon_first'] = s1.P_Date_6mon.astype('datetime64[M]')

s2 = pd.merge(s1, sales, how='left', left_on=['chc', 'P_Date_6mon_first'], \
              right_on=['chc', 'month_sales'])

# Note 'status' doesn't exactly match 'revenue_m0'.
s2['status2'] = np.where((s2.churn_time_in_day >= s2.P_Date_6mon_first) &\
                         (s2.revenue_m0 > 0), 'ACTIVE', s2.status)
s2['Last_Revenue'] = np.where(s2.revenue_m0 <= 0, np.nan, s2.revenue_m0)


# Survival Rate in 6 Months
pivot1 = pd.pivot_table(s2,
                        index   = 'status2',
                        columns = 'First_Offer',
                        values  = 'chc', 
                        aggfunc = 'count').fillna(0)
pivot1.to_csv('Callbacks_status_seg.csv', index=True)



s3 = s2.groupby(['First_Offer']).agg({'Calls_Count': ['count', 'sum', 'mean'],
               'Offers_Count':['sum', 'mean'],
               'Offers_Sum':['sum', ],
               'Save_Revenue': ['count', 'sum', 'mean'],
               'Last_Revenue': ['count', 'sum', 'mean']})
s3.columns = ['First_Offer_Count', 'Total_Call_Count', 'Avg_Call_Count', 
              'Total_Offer_Count', 'Avg_Offer_Count', 'Total_Offer_Amt',
              'Save_Revenue_Count', 'Save_Revenue_Sum', 'Save_Revenue_Avg',
              'Last_Revenue_Count', 'Last_Revenue_Sum', 'Last_Revenue_Avg']
#s3['Dollars_per_Call'] = s3.Total_Offer_Amt/s3.Total_Call_Count
#s3['Dollars_per_Offer'] = s3.Total_Offer_Amt/s3.Total_Offer_Count
s3['First_Offer'] = s3.index
var_list = ['First_Offer'] + list(s3)[:-1]
s3 = s3[var_list]
s3.to_csv('Callbacks_seg.csv', index=True)
