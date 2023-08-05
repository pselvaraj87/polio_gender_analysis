import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import shapefile as shp  # Requires the pyshp package
from matplotlib.ticker import FormatStrFormatter

df_fata = pd.read_excel('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/FATA TDP ERP - Finalized Geo.xlsx')
df_fata.dropna(subset=['latitude'], inplace=True)
df_fata['latitude'] = df_fata['latitude'].apply(lambda x: float(x.split('°')[0]))
df_fata['longitude'] = df_fata['longitude'].apply(lambda x: float(x.split('°')[0]))

if not os.path.exists('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv/pak_rpe_2021_09_age_0_5_nonzero.csv'):
    df_raster = pd.read_csv('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv/pak_rpe_2021_09_age_0_5.csv')

    df_raster = df_raster[~(df_raster['pop']==0)]
    df_raster.to_csv('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv/pak_rpe_2021_09_age_0_5_nonzero.csv')

else:
    df_raster = pd.read_csv('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv/pak_rpe_2021_09_age_0_5_nonzero.csv')

df_grid = pd.read_csv('/Users/prashanthselvaraj/Github/polio_gender_analysis/data/raster_csv/KP_grid.csv')

df_raster['alphas'] = df_raster['pop']/max(df_raster['pop'])

rgba_colors_raster = np.zeros((len(df_raster), 4))
rgba_colors_raster[:, 3] = df_raster['pop']/max(df_raster['pop'])

rgba_colors_grid = np.zeros((len(df_grid), 4))
rgba_colors_grid[:, 3] = df_grid['pop']/(max(df_grid['pop'])*1.2) + 0.1

fig = plt.figure(figsize=(5, 6))
ax = plt.subplot(111,aspect = 'equal')
# plt.scatter(df_raster['longitude'], df_raster['latitude'], marker='s', s=0.5, color=rgba_colors_raster)
ax.scatter(df_grid['lon'], df_grid['lat'], marker='s', s=10, color=rgba_colors_grid)
ax.scatter(df_fata['longitude'], df_fata['latitude'], marker='o', color='r', s=20)
ax.set_xlim([69, 72])
ax.set_ylim([31, 35])
ax.text(0.22, 0.95, 'Prashanth Selvaraj\nIDM, BMGF', transform=ax.transAxes,
        fontsize=10, color='k', alpha=0.5,
        ha='center', va='center')


cmap = plt.get_cmap('Greys', 100)
norm = matplotlib.colors.Normalize(vmin=0, vmax=1)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ticks=np.linspace(0.0, 1.0, 6), boundaries=np.linspace(0.0, 1.0, 6),
                    fraction=0.05, pad=0.04, label='Population')
ticklabels = list(np.linspace(min(df_grid['pop']), max(df_grid['pop']), 6))
ticklabels = [int(x) for x in ticklabels]
cbar.set_ticklabels(ticklabels)

plt.tight_layout()
# plt.show()

plt.savefig('/Users/prashanthselvaraj/Github/polio_gender_analysis/figures/0_pop_scatter_grid_0_5.png')
# plt.savefig('/Users/prashanthselvaraj/Github/polio_gender_analysis/figures/0_pop_scatter_0_5.png')
#
# plt.show()



# sf = shp.Reader("/Users/prashanthselvaraj/Github/polio_gender_analysis/data/PAK_Rapid_Population_Estimate_Total/pak_rpe_2021_09/pak_rpe_2021_09.shp")
#
# plt.figure()
# for shape in sf.shapeRecords():
#     x = [i[0] for i in shape.shape.points[:]]
#     y = [i[1] for i in shape.shape.points[:]]
#     plt.plot(x,y)
# plt.show()




