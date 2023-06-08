import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

# Run govt_data.py first

df_kids = pd.read_csv('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/govt_kids.csv')
df_parents = pd.read_csv('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/govt_parents.csv')
fig_dir = '/Users/prashanthselvaraj/Github/polio_gender_analysis/figures'
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
    plt.title('Govt. raster_data')
    plt.savefig(os.path.join(fig_dir, f'{c}-govt.png'))
    plt.close('all')
    # sns.barplot(raster_data=df, x="age", y="counts", hue=c, errorbar="sd")
    # plt.ylabel(['Number per age group'])
    # plt.show()


# plot mum's status vs vaccination
channels = dict(zip(['sc1q1a', 'sc1q01', 'sc1q05', 'sc2q01', 'sc2q05', 'sc2q08', 'sc2q11', 'seaq01', 'seaq03'],
                    ['Can read', 'Education background', 'Highest grade', 'Have you used:', 'Personal phone',
                     'Internet last 3 months', 'Internet last 12 months', 'Work', 'Enterprise']))

vaccination_key_x_axis = dict(zip([i for i in range(1, 5)],
                          ['Yes, on card', 'Yes, according\nto memory', 'No', 'Yes, By Polio\ncampaign']))

df_parents.rename(columns=polio_channels, inplace=True)
df_parents.rename(columns=channels, inplace=True)

answer_key = {'Can read': {1: 'Yes', 2: 'No'}, 'Education background': {1: 'Never attended', 2: 'Attended school',
                                                                        3: 'Currently attending'},
              'Have you used:': {1: 'Desktop', 2: 'Laptop', 3: 'Tablet', 4: 'Other', 5: 'None'},
              'Personal phone': {1: 'Mobile', 2: 'Smart', 3: 'None'},
              'Internet last 3 months': {1: 'Yes', 2: 'No'}, 'Internet last 12 months': {1: 'Yes', 2: 'No'},
              'Work': {1: 'Yes', 2: 'No'}, 'Enterprise': {1: 'Yes', 2: 'No,\nseeking work', 3:'No,\nnot seeking'}}


# for p in ['mom']:
for x in ['by_channel', 'by_vax_type']:
# for x in ['by_vax_type']:
    for p in ['mom']:
    # for p in ['mom', 'dad']:
        for sc in ['Can read', 'Education background', 'Highest grade', 'Have you used:', 'Personal phone',
                         'Internet last 3 months', 'Internet last 12 months', 'Work', 'Enterprise']:
        # for sc in ['Personal phone',
        #            ]:
            for i, c in enumerate(['Polio 0', 'Polio 1', 'Polio 2', 'Polio 3', 'IPV']):
                dftemp = df_parents[df_parents['Parent']==p]
                df = dftemp.groupby([sc, c]).size().reset_index(name='counts')
                df[c] = df[c].apply(lambda x: vaccination_key_x_axis[x])
                if sc in answer_key:
                    df[sc] = df[sc].apply(lambda x: answer_key[sc][x])
                    if x == 'by_channel':
                        df['%'] = 100 * df['counts'] / df.groupby(sc)['counts'].transform('sum')
                        sns.barplot(data=df, x=sc, y="%", hue=c, errorbar="sd")
                        plt.ylabel(f'Percentage of {p}s - {sc}')
                        plt.title(f'Govt. raster_data: {p}s - {sc}')
                    else:
                        df['%'] = 100 * df['counts'] / df.groupby(c)['counts'].transform('sum')
                        sns.barplot(data=df, x=c, y="%", hue=sc, errorbar="sd")
                        plt.ylabel(f'Percentage of {p}s - {c}')
                        plt.title(f'Govt. raster_data: {p}s - {c}')
                    plt.ylim([0, 100])
                else:
                    df[sc] = df[sc].astype(int)
                    if x == 'by_channel':
                        df['%'] = 100 * df['counts'] / df.groupby(sc)['counts'].transform('sum')

                        ax = sns.barplot(data=df, x=sc, y="%", hue=c, errorbar="sd")

                        ax.set_ylabel(f'Percentage of {p}s - {sc}')
                        ax.set_title(f'Govt. raster_data: {p}s - {sc}')

                    else:
                        df['%'] = 100 * df['counts'] / df.groupby(c)['counts'].transform('sum')
                        norm = plt.Normalize(dftemp[sc].min(), dftemp[sc].max())
                        sm = plt.cm.ScalarMappable(cmap="Blues", norm=norm)
                        sm.set_array([])

                        ax = sns.barplot(data=df, x=c, y="%", hue=sc, palette='Blues')

                        ax.set_ylabel(f'Percentage of {p}s - {c}')
                        ax.set_title(f'Govt. raster_data: {p}s - {c}')
                        ax.get_legend().remove()

                        cbar = ax.figure.colorbar(sm)
                        cbar.ax.set_ylabel('Highest grade', rotation=270, labelpad=15)
                        cbar.ax.set_ylim([0, 28])
                        cbar.ax.get_yaxis().set_ticks([0, 7, 14, 21, 28])

                # sns.barplot(raster_data=df, x=sc, y="%", hue=c, errorbar="sd")
                sc_string = sc.replace(' ', '_')
                # plt.show()
                plt.savefig(os.path.join(fig_dir, f'{p}-{sc_string}-{c}-govt_{x}.png'))
                plt.close('all')
