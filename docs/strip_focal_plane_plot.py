import yaml
import matplotlib.pylab as plt

with open('../instrument/strip_focal_plane.yaml', 'rt') as f:
    focal_plane = yaml.load(f)

points = [(x['orientation'][0], x['orientation'][1], key, x['color'])
          for key, x in focal_plane.items()]
plt.scatter(x=[x[0] for x in points],
            y=[x[1] for x in points],
            color=[x[3] for x in points],
            s=500, alpha=0.8)

for pt in points:
    plt.text(pt[0], pt[1], pt[2],
             horizontalalignment='center',
             verticalalignment='center')

plt.savefig('strip_focal_plane_plot.svg')
