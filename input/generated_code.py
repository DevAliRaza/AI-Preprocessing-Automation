import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pandas_profiling import ProfileReport
df = df.drop_duplicates()
numeric_cols = df.select_dtypes(include=[np.number]).columns
categorical_cols = df.select_dtypes(include=[object]).columns
df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
df[categorical_cols] = df[categorical_cols].astype('category')
for col in numeric_cols:
    df[col].fillna(df[col].median(), inplace=True)
for col in categorical_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)
for col in df.columns:
    if 'date' in col.lower():
        try:
            df[col] = pd.to_datetime(df[col])
        except:
            pass
for col in numeric_cols:
    df.boxplot(column=col)
    plt.savefig('boxplot_' + col + '.png')
    plt.close()
for col in numeric_cols:
    df[col].hist()
    plt.savefig('histogram_' + col + '.png')
    plt.close()
plt.figure(figsize=(12,10))
sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f")
plt.savefig('report.pdf')
missing_values = df.isnull().sum().reset_index()
missing_values.columns = ['column_name', 'missing_count']
missing_values['missing_ratio'] = missing_values['missing_count'] / len(df)
missing_values.to_csv('missing_values_report.csv',index = False)
profile = ProfileReport(df, title='YData Profiling Report')
profile.to_file('profile_report.html')
df.to_csv('processed_data.csv', index=False)