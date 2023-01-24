import os
import pandas as pd

data_dir = '/Users/pselvaraj/Github/polio_gender_analysis/data/govt_data'

# children
f = 'plist.dta'
df = pd.read_stata(os.path.join(data_dir, f), convert_categoricals=False)
df = df[df['province'] == 1]
df_kids = df[df['age'] < 5]
df_kids = df_kids[['hhcode', 'idc', 'sb1q4', 'age', 'sb1q9', 'sb1q10']]

f = 'seci.dta'
df_i = pd.read_stata(os.path.join(data_dir, f), convert_categoricals=False)
df_i = df_i[df_i['province'] == 1]
df_i = df_i[['hhcode', 'idc', 'siaq03', 'siaq5a', 'siaq5b', 'siaq5c', 'siaq5d', 'siaq5e', 'siaq5f', 'siaq5g', 'siaq5h',
             'siaq5i', 'siaq5j', 'siaq5k', 'siaq5l', 'siaq5m', 'siaq5n']]

f = 'secc1.dta'
df_c1 = pd.read_stata(os.path.join(data_dir, f), convert_categoricals=False)
df_c1 = df_c1[df_c1['province'] == 1]
df_c1 = df_c1[['hhcode', 'idc', 'sc1q1a', 'sc1q01', 'sc1q05']]

f = 'secc2.dta'
df_c2 = pd.read_stata(os.path.join(data_dir, f), convert_categoricals=False)
df_c2 = df_c2[df_c2['province'] == 1]
df_c2 = df_c2[['hhcode', 'idc', 'sc2q01', 'sc2q05', 'sc2q08', 'sc2q11']]

f = 'sece.dta'
df_e = pd.read_stata(os.path.join(data_dir, f), convert_categoricals=False)
df_e = df_e[df_e['province'] == 1]
df_e = df_e[['hhcode', 'idc', 'seaq01', 'seaq03', 'seaq10']]

# Merge datasets
df_kids = pd.merge(df_kids, df_i, on=['hhcode', 'idc'])
df_kids.to_csv('/Users/pselvaraj/Github/polio_gender_analysis/data/govt_kids.csv')

# Parents
df_moms = df_kids[['hhcode', 'sb1q10', 'siaq03', 'siaq5a', 'siaq5b', 'siaq5c', 'siaq5d', 'siaq5e', 'siaq5f', 'siaq5g', 'siaq5h',
             'siaq5i', 'siaq5j', 'siaq5k', 'siaq5l', 'siaq5m', 'siaq5n']]
df_moms.rename(columns={'sb1q10': 'idc'}, inplace=True)
df_moms['Parent'] = ['mom']*len(df_moms)
df_dads = df_kids[['hhcode', 'sb1q9', 'siaq03', 'siaq5a', 'siaq5b', 'siaq5c', 'siaq5d', 'siaq5e', 'siaq5f', 'siaq5g', 'siaq5h',
             'siaq5i', 'siaq5j', 'siaq5k', 'siaq5l', 'siaq5m', 'siaq5n']]
df_dads.rename(columns={'sb1q9': 'idc'}, inplace=True)
df_dads['Parent'] = ['dad']*len(df_dads)
df_parents = pd.concat([df_dads, df_moms])
df_parents = df_parents[~df_parents['idc'].isin([98, 99])]
df_parents = pd.merge(df_parents, df_c1, on=['hhcode', 'idc'])
df_parents = pd.merge(df_parents, df_c2, on=['hhcode', 'idc'])
df_parents = pd.merge(df_parents, df_e, on=['hhcode', 'idc'])
df_parents.to_csv('/Users/pselvaraj/Github/polio_gender_analysis/data/govt_parents.csv')