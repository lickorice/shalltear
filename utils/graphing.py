import matplotlib.pyplot as plt


def plot_graph(x_pts, y_pts, title, graph_name):
    plt.clf()
    
    # plt.plot(x_pts, y_pts)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.plot(x_pts, y_pts, linewidth=5.0, color="#e73895")

    ax.spines['left'].set_color('#dddddd')
    ax.spines['right'].set_color('#dddddd')
    ax.spines['top'].set_color('#dddddd')
    ax.spines['bottom'].set_color('#dddddd')

    ax.tick_params(axis="y" , colors="#dddddd")
    ax.tick_params(axis="x" , colors="#dddddd", labelbottom=False)

    plt.savefig(graph_name, transparent=True)
