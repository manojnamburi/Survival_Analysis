# -*- coding: utf-8 -*-
"""
Author: Taesun Kim
Date:   1/25/2019

Title: Model Single Call Customers

Purpose:
    1. Develope Survival Curves.
    2. Compre Survival Curves by Erosion Group.

Input: 
    1. 'data_survival.pickle'

Output: 

References:    
    https://lifelines.readthedocs.io/en/latest/index.html
    http://savvastjortjoglou.com/nfl-survival-analysis-kaplan-meier.html

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





### 1. Select Customers with a Single Call.
#with open('data_survival.pickle', 'wb') as f:
#    pickle.dump(df4, f, pickle.HIGHEST_PROTOCOL)

#import pickle
with open('data_survival.pickle', 'rb') as f:
    data_survival = pickle.load(f)

# For Some REASONS, 'duration' is saved in string. Convert it to interger.
data_survival['duration_in_month'] = data_survival['duration_in_month'].astype('int')
data_survival['duration_in_week']  = data_survival['duration_in_week'].astype('int')
data_survival['duration_in_day']   = data_survival['duration_in_day'].astype('int')

data_survival['Erosion_Int']   = data_survival['Erosion'].round().astype('int')
data_survival['Erosion_Pct_Int']   = data_survival['Erosion_Pct'].round().astype('int')

# Re-group Important Erosion Values
#https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html
data_survival['Erosion_Rep']   =  data_survival.Erosion_Int.replace(\
             [4, 6, 9, 11, 14, 16, 19, 21, 24, 26, 29, 31, 34, 36, 39, 41], \
             [5, 5, 10, 10, 15, 15, 20, 20, 25, 25, 30, 30, 35, 35, 40, 40])




# 0. Remove Duplicated Records
# Note that df.drop_duplicates(keep = False) exclude all duplicates.
data = data_survival.copy()    
data = data.drop_duplicates()

# Include Customers with a Single Call over 1/2017 - 09/2018
df_call_count = data['chc'].value_counts().to_frame().reset_index()
df_call_count.columns = ['chc', 'call_count']


# 1. Select Customers with a Single Call Only!
df = pd.merge(data, df_call_count, how = 'inner', on = 'chc')
row_select = (df['call_count'] == 1)
df = df.loc[row_select]
# df.call_count.value_counts()
# df.chc.unique().size

# tmp = df.loc[df['duration_in_month'] == 0]


# Check the Frequency of Erosion
df.Erosion_bin1.value_counts().sort_index().to_csv('Erosion_Freq1.csv')
df.Erosion_bin2.value_counts().sort_index().to_csv('Erosion_Freq2.csv')
df.Erosion_Int.value_counts().sort_index().to_csv('Erosion_Freq3.csv')
df.Erosion_Rep.value_counts().sort_index().to_csv('Erosion_Freq4.csv')
df.Erosion_Pct_bin1.value_counts().sort_index().to_csv('Erosion_Pct_Freq1.csv')
df.Erosion_Pct_bin2.value_counts().sort_index().to_csv('Erosion_Pct_Freq2.csv')
df.Erosion_Pct_Int.value_counts().sort_index().to_csv('Erosion_Pct_Freq3.csv')





### 2. Estimate Survival Curves
#df.duration_in_month.describe()
#df.duration_in_month.value_counts().sort_index()
#ax0 = plt.figure(figsize=(10,5))
#f, ax0 = plt.subplots(1, 1, figsize=(15,10))

##  Use the Kaplan-Meier Estimator
from lifelines import KaplanMeierFitter
kmf = KaplanMeierFitter()

fig0, ax0 = plt.subplots(1, 1, figsize = (10, 6))

## All Churners
kmf1 = KaplanMeierFitter()
kmf1.fit(durations = df['duration_in_month'], 
        event_observed = df['churn_all'], 
        label = 'Survival Plot: All Churn Types')
kmf1.plot(ax = ax0)


## Voluntary Churners
kmf2 = KaplanMeierFitter()
kmf2.fit(durations = df['duration_in_month'], 
        event_observed = df['churn_voluntary'], 
        label = 'Survival Plot: Voluntary Churn')
kmf2.plot(ax = ax0)

ax0.set_xlim(0, 25)
ax0.set_ylim(0.5, 1)
plt.title("The Kaplan-Meier Estimate for Altice Customers\n(01/2017 - 09/2018)")
plt.ylabel("Probability an Altice Customer is Still Active")


## Event Tables
table1 = kmf1.event_table
table2 = kmf2.event_table
tables = pd.merge(table1, table2, left_index=True, right_index=True,\
                  suffixes=["_all", "_voluntary"])
#tables = pd.concat([table1, table2], axis = 1)


## Survival Tables
survival1 = kmf1.survival_function_
survival2 = kmf2.survival_function_
survivals = pd.merge(survival1, survival2, left_index=True, right_index=True,\
                  suffixes=["_all", "_voluntary"])
#survivals = pd.concat([survival1, survival2], axis = 1)

#kmf._conditional_time_to_event_()
#print(kmf.median_)


## All Churners
#  By Erosion
kmf = KaplanMeierFitter()
table_surv = kmf1.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_bin1'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_all'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf1.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_All_Erosion1.csv')


kmf = KaplanMeierFitter()
table_surv = kmf1.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_bin2'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_all'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf1.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_All_Erosion2.csv')


kmf = KaplanMeierFitter()
table_surv = kmf1.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_Int'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_all'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf1.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_All_Erosion3.csv')


kmf = KaplanMeierFitter()
table_surv = kmf1.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_Rep'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_all'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf1.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_All_Erosion4.csv')



# By Erosion Pct
table_surv = kmf1.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_Pct_bin2'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_all'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf1.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_All_Erosion_Pct.csv')


table_surv = kmf1.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_Pct_Int'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_all'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf1.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_All_Erosion_Pct2.csv')




## Voluntary Churners
#  By Erosion
table_surv = kmf2.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_bin1'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_voluntary'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf2.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_Voluntary_Erosion.csv')


# By Erosion Pct
table_surv = kmf2.survival_function_
dfs = []

fig0, ax0 = plt.subplots(1, 1, figsize = (20, 12))
for name, df_group in df.groupby('Erosion_Pct_bin2'):
    kmf.fit(durations      = df_group['duration_in_month'], 
            event_observed = df_group['churn_voluntary'], label = name)
    kmf.plot(ax=ax0, ci_show=False)
    dfs.append(kmf.survival_function_)

kmf2.plot(ax = ax0, ci_show=False)

for survF in dfs:
    table_surv = pd.concat([table_surv, survF], axis=1)
table_surv.to_csv('Survival Functions_Voluntary_Erosion_Pct.csv')





### 3. Test Survival Curves
from lifelines.statistics import logrank_test
import itertools as it

list_group = np.arange(0, 45, 5).tolist()


## All Churners by Erosion Level
list_test_results   = []

p_values = list()
for i, j in it.combinations(list_group, 2):
    results = logrank_test(
            df.loc[df['Erosion_Int'] == i ]['duration_in_month'],
            df.loc[df['Erosion_Int'] == j ]['duration_in_month'],
            event_observed_A = df.loc[df['Erosion_Int'] == i ]['churn_all'],
            event_observed_B = df.loc[df['Erosion_Int'] == j ]['churn_all'])
    df_dict = {
            'Ersion_A': [str(i)],
            'Ersion_B': [str(j)],
            'test_statistic': [results.test_statistic],
            'p_value': [results.p_value]
            }
    df_results = pd.DataFrame(df_dict)
    list_test_results.append(df_results)

table_test_results = pd.DataFrame(columns = ['Ersion_A', 'Ersion_B', 'test_statistic', 'p_value'])

for test_result in list_test_results:
    table_test_results = pd.concat([table_test_results, test_result], axis = 0)


pivot1 = pd.pivot_table(table_test_results,
                        index   = 'Ersion_A',
                        columns = 'Ersion_B',
                        values  = 'p_value', 
                        aggfunc = 'mean').fillna('')

list_row = list(map(str, list_group[:-1]))
list_col = list(map(str, list_group[1:]))
pivot1.loc[list_row, list_col].to_csv('test_results_all_Erosion.csv')


## All Churners by Adjusted Erosion Level
list_group = np.arange(0, 45, 5).tolist()
list_test_results   = []

p_values = list()
for i, j in it.combinations(list_group, 2):
    results = logrank_test(
            df.loc[df['Erosion_Rep'] == i ]['duration_in_month'],
            df.loc[df['Erosion_Rep'] == j ]['duration_in_month'],
            event_observed_A = df.loc[df['Erosion_Rep'] == i ]['churn_all'],
            event_observed_B = df.loc[df['Erosion_Rep'] == j ]['churn_all'])
    df_dict = {
            'Ersion_A': [str(i)],
            'Ersion_B': [str(j)],
            'test_statistic': [results.test_statistic],
            'p_value': [results.p_value]
            }
    df_results = pd.DataFrame(df_dict)
    list_test_results.append(df_results)

table_test_results = pd.DataFrame(columns = ['Ersion_A', 'Ersion_B', 'test_statistic', 'p_value'])

for test_result in list_test_results:
    table_test_results = pd.concat([table_test_results, test_result], axis = 0)


pivot1 = pd.pivot_table(table_test_results,
                        index   = 'Ersion_A',
                        columns = 'Ersion_B',
                        values  = 'p_value', 
                        aggfunc = 'mean').fillna('')

list_row = list(map(str, list_group[:-1]))
list_col = list(map(str, list_group[1:]))
pivot1.loc[list_row, list_col].to_csv('test_results_all_Erosion2.csv')



## All Churners by Erosion Percentage
list_group = np.arange(0, 22, 1).tolist()
list_test_results   = []

p_values = list()
for i, j in it.combinations(list_group, 2):
    results = logrank_test(
            df.loc[df['Erosion_Pct_Int'] == i ]['duration_in_month'],
            df.loc[df['Erosion_Pct_Int'] == j ]['duration_in_month'],
            event_observed_A = df.loc[df['Erosion_Pct_Int'] == i ]['churn_all'],
            event_observed_B = df.loc[df['Erosion_Pct_Int'] == j ]['churn_all'])
    df_dict = {
            'Ersion_A': [str(i)],
            'Ersion_B': [str(j)],
            'test_statistic': [results.test_statistic],
            'p_value': [results.p_value]
            }
    df_results = pd.DataFrame(df_dict)
    list_test_results.append(df_results)

table_test_results = pd.DataFrame(columns = ['Ersion_A', 'Ersion_B', 'test_statistic', 'p_value'])

for test_result in list_test_results:
    table_test_results = pd.concat([table_test_results, test_result], axis = 0)


pivot1 = pd.pivot_table(table_test_results,
                        index   = 'Ersion_A',
                        columns = 'Ersion_B',
                        values  = 'p_value', 
                        aggfunc = 'mean').fillna('')

list_row = list(map(str, list_group[:-1]))
list_col = list(map(str, list_group[1:]))
pivot1.loc[list_row, list_col].to_csv('test_results_all_Erosion_Pct.csv')