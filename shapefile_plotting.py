import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd


def change_text(x):
    if x == 'D. I. Khan':
        return x
    elif ' ' in x:
        return x.split(' ')[0] + '\n'  + x.split(' ')[1]
    else:
        return x


def alpha_blending(hex_color, alpha) :
    """ alpha blending as if on the white background.
    """
    foreground_tuple  =  matplotlib.colors.hex2color(hex_color)
    foreground_arr = np.array(foreground_tuple)
    final = tuple( (1. -  alpha) + foreground_arr*alpha )

    return(final)

sf = gpd.read_file("/Users/prashanthselvaraj/Github/polio_gender_analysis/data/shape_files/pak_admbnda_adm2_wfp_20220909.shp")

# find KP indices:
sf = sf[sf['ADM1_EN'] == 'Khyber Pakhtunkhwa']
sf['coords'] = sf['geometry'].apply(lambda x: x.representative_point().coords[:])
sf['coords'] = [coords[0] for coords in sf['coords']]

df = pd.read_csv('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/Coverage_by_district.csv')
df.rename(columns={'District ': 'ADM2_EN'}, inplace=True)

sf3 = pd.merge(sf, df, on='ADM2_EN', how='right')
sf3['Alpha'] = sf3['Alpha'].apply(lambda x: eval(x.split('%')[0])/100)
sf3['color'] = sf3['Alpha'].apply(lambda x: alpha_blending('#FF0000', 0.1+x*0.8))

plt.figure(figsize=(8, 8))
gax = sf3.plot(color=sf3['color'], figsize=(6, 8), edgecolor="black")
sf3['ADM2_EN'] = sf3['ADM2_EN'].apply(lambda x: change_text(x))
for idx, row in sf3.iterrows():
    gax.annotate(text=row['ADM2_EN'], xy=row['coords'],
                 horizontalalignment='center')

cmap = plt.get_cmap('Reds', 100)
norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ticks=np.linspace(0.1, 0.7, 6), boundaries=np.linspace(0.1, 0.7, 6),
                    fraction=0.05, pad=0.04, label='Crude Coverage (OPV0)')
cbar.set_ticklabels([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
# cbar.set_clim(-2.0, 2.0)

df_fata = pd.read_excel('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/FATA TDP ERP - Finalized Geo.xlsx')
df_fata.dropna(subset=['latitude'], inplace=True)
df_fata['latitude'] = df_fata['latitude'].apply(lambda x: float(x.split('°')[0]))
df_fata['longitude'] = df_fata['longitude'].apply(lambda x: float(x.split('°')[0]))
plt.scatter(df_fata['longitude'], df_fata['latitude'], marker='o', color='blue', s=10)
plt.xlim([69, 72])
plt.ylim([31, 35])

plt.savefig('/Users/prashanthselvaraj/Github/polio_gender_analysis/figures/0_KP.png')
plt.show()
