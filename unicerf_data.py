import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

data_dir = '/Users/pselvaraj/Github/polio_gender_analysis/data/unicef_data'
fig_dir = '/Users/pselvaraj/Github/polio_gender_analysis/figures'
os.makedirs(fig_dir, exist_ok=True)

# children
f = 'ch.sav'
df_kids = pd.read_spss(os.path.join(data_dir, f), convert_categoricals=False)
df_kids = df_kids[['UF1', 'UF2', 'UF3', 'UF4', 'UB2', 'IM6P0D', 'IM6P1D', 'IM6P2D', 'IM6P3D', 'IM6ID']]
labels = ['cluster', 'household', 'name', 'mom', 'age', 'Polio 0', 'Polio 1', 'Polio 2', 'Polio 3', 'IPV']
rename_cols = dict(zip(['UF1', 'UF2', 'UF3', 'UF4', 'UB2', 'IM6P0D', 'IM6P1D', 'IM6P2D', 'IM6P3D', 'IM6ID'], labels))
df_kids.rename(columns=rename_cols, inplace=True)
df_kids[['Polio 0', 'Polio 1', 'Polio 2', 'Polio 3', 'IPV']] = df_kids[['Polio 0', 'Polio 1', 'Polio 2', 'Polio 3', 'IPV']].notnull().astype('int')

vaccination_key = dict(zip([i for i in range(2)],
                          ['No', 'Yes']))
for c in ['Polio 0', 'Polio 1', 'Polio 2', 'Polio 3', 'IPV']:
    df = df_kids.groupby(['age', c]).size().reset_index(name='counts')
    df[c] = df[c].apply(lambda x: vaccination_key[x])
    df['%'] = 100 * df['counts'] / df.groupby('age')['counts'].transform('sum')
    sns.barplot(data=df, x="age", y="%", hue=c, errorbar="sd")
    plt.ylabel('Percentage of age group')
    plt.title('UNICEF data')
    plt.savefig(os.path.join(fig_dir, f'{c}-unicef.png'))
    plt.close('all')
    # sns.barplot(data=df, x="age", y="counts", hue=c, errorbar="sd")
    # plt.ylabel(['Number per age group'])
    # plt.show()

# women
# f = 'wm.sav'
# df_w = pd.read_spss(os.path.join(data_dir, f), convert_categoricals=False)
# df_w = df_w[['HH1', 'HH2', 'WM3', 'WB6', 'MT5', 'MT10', 'MT12']]