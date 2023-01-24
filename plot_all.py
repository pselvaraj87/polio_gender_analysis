import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Run govt_data.py first

df_kids = pd.read_csv('/Users/pselvaraj/Github/polio_gender_analysis/data/govt_kids.csv')
df_parents = pd.read_csv('/Users/pselvaraj/Github/polio_gender_analysis/data/govt_parents.csv')
fig_dir = '/Users/pselvaraj/Github/polio_gender_analysis/figures'
os.makedirs(fig_dir, exist_ok=True)

polio_channels = dict(zip(['siaq5h', 'siaq5i', 'siaq5j', 'siaq5k', 'siaq5l'],
                          ['Polio 0', 'Polio 1', 'Polio 2', 'Polio 3', 'IPV']))
vaccination_key = dict(zip([i for i in range(1, 5)],
                          ['Yes, on card', 'Yes, according to memory', 'No', 'Yes, By Polio campaign']))

# plot kids vaccination - polio
df_kids.rename(columns=polio_channels, inplace=True)
for c in ['Polio 0', 'Polio 1', 'Polio 2', 'Polio 3', 'IPV']:
    df = df_kids.groupby(['age', c]).size().reset_index(name='counts')
    df[c] = df[c].apply(lambda x: vaccination_key[x])
    df['%'] = 100 * df['counts'] / df.groupby('age')['counts'].transform('sum')
    sns.barplot(data=df, x="age", y="%", hue=c, errorbar="sd")
    plt.ylabel('Percentage of age group')
    plt.title('Govt. data')
    plt.savefig(os.path.join(fig_dir, f'{c}-govt.png'))
    plt.close('all')
    # sns.barplot(data=df, x="age", y="counts", hue=c, errorbar="sd")
    # plt.ylabel(['Number per age group'])
    # plt.show()


# plot mum's status vs vaccination
channels = dict(zip(['sc1q1a', 'sc1q01', 'sc1q05', 'sc2q01', 'sc2q05', 'sc2q08', 'sc2q11', 'seaq01', 'seaq03'],
                    ['Can read', 'Education background', 'Highet grade', 'Have you used:', 'Personal phone',
                     'Internet last 3 months', 'Internet last 12 months', 'Work', 'Shop/business/farm']))

