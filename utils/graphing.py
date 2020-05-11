import matplotlib.pyplot as plt


def plot_graph(x_pts, y_pts, title, graph_name):
    plt.clf()
    plt.title(title, fontsize=8)
    
    plt.plot(x_pts, y_pts)

    plt.xticks(fontsize=6)
    plt.yticks(fontsize=6)

    for x, y in zip(x_pts, y_pts):
        label = "{:.2f}".format(y)
        plt.annotate(
            label,
            (x,y),
            fontsize=6,
            textcoords="offset points",
            xytext=(0,10),
            ha='center'
        )

    plt.savefig(graph_name)