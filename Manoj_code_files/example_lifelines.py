# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 14:50:09 2019

@author: TKIM
See https://lifelines.readthedocs.io/en/latest/index.html
"""



### Kaplan-Meier and Nelson-Aalen
from lifelines.datasets import load_waltons
df = load_waltons() # returns a Pandas DataFrame
print(df.head())

from lifelines import KaplanMeierFitter
kmf = KaplanMeierFitter()
kmf.fit(T, event_observed=E)  # or, more succinctly, kmf.fit(T, E)

kmf.survival_function_
kmf.median_
kmf.plot()


# Multiple Groups
groups = df['group']
ix = (groups == 'miR-137')

kmf.fit(T[~ix], E[~ix], label='control')
ax = kmf.plot()

kmf.fit(T[ix], E[ix], label='miR-137')
ax = kmf.plot(ax=ax)


# Alternative Methods
ax = plt.subplot(111)
kmf = KaplanMeierFitter()
for name, grouped_df in df.groupby('group'):
    kmf.fit(grouped_df["T"], grouped_df["E"], label=name)
    kmf.plot(ax=ax)

    
from lifelines import NelsonAalenFitter
naf = NelsonAalenFitter()
naf.fit(T, event_observed=E)



### Getting Data in The Right Format
from lifelines.utils import datetimes_to_durations
# start_times is a vector of datetime objects
# end_times is a vector of (possibly missing) datetime objects.
T, E = datetimes_to_durations(start_times, end_times, freq='h')

from lifelines.utils import survival_table_from_events
table = survival_table_from_events(T, E)
print(table.head())



### Survival Regression
from lifelines.datasets import load_regression_dataset
regression_dataset = load_regression_dataset()

regression_dataset.head()

from lifelines import CoxPHFitter

# Using Cox Proportional Hazards model
cph = CoxPHFitter()
cph.fit(regression_dataset, 'T', event_col='E')
cph.print_summary()
cph.plot()


# Using Aalen's Additive model
from lifelines import AalenAdditiveFitter
aaf = AalenAdditiveFitter(fit_intercept=False)
aaf.fit(regression_dataset, 'T', event_col='E')

X = regression_dataset.drop(['E', 'T'], axis=1)
aaf.predict_survival_function(X.iloc[10:12]).plot()  # get the unique survival functions of two subjects

aaf.plot()