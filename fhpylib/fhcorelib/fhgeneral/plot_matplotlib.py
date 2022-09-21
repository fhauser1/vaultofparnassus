import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random

# import matplotlib.mlab as mlab
from matplotlib.ticker import NullFormatter
# from mpl_toolkits.axes_grid1 import make_axes_locatable


def mplbarplot(bardata,labels_tup,figname='defaultbarplotname.pdf',resolution = 150):
    N=len(bardata)
    ind = [i-0.5 for i in range(0,N)]  # the x locations for the groups
    width = 0.35
    fig = plt.figure()

    plt.rcParams['font.size'] = 20
    ax = fig.add_subplot(111)
    ax.tick_params(labelsize=20)
    
    ax.axis([-0.5,N-0.5,0,max(bardata)+1])
    ax.bar(ind,bardata,width=0.35,color=labels_tup[3])
    ax.set_ylabel(labels_tup[0])
    ax.set_xlabel(labels_tup[1])
    ax.set_xticklabels( labels_tup[2] )
    ax.set_xticks([ele+0.2 for ele in ind]) 
    figfi = open(figname,'wb')
    plt.savefig(figfi,dpi = resolution,format='pdf')
    figfi.close()
    plt.close()
    



def mplhistogram(valuelis,binno = None,figname='defaulhistogramtplotname.pdf',xlabel='xaxis',ylabel='yaxis',resolution=150,grid_show=False):
    """ valuelis: list with all the values"""
    'binnno: number or also list i.e.  bins = [100,125,150,160,170,180,190,200,210,220,230,240,250,275,300]'
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # the histogram of the data
    
    if binno:
        n, bins, patches = ax.hist(valuelis, binno, normed=1, facecolor='green', alpha=0.75)
    else:
        n, bins, patches = ax.hist(valuelis,  normed=1, facecolor='green', alpha=0.75)
        

    # hist uses np.histogram under the hood to create 'n' and 'bins'.
    # np.histogram returns the bin edges, so there will be 50 probability
    # density values in n, 51 bin edges in bins and 50 patches.  To get
    # everything lined up, we'll compute the bin centers
    bincenters = 0.5*(bins[1:]+bins[:-1])
    # add a 'best fit' line for the normal PDF
    
    # y = mlab.normpdf( bincenters, mu, sigma)
    # l = ax.plot(bincenters, y, 'r--', linewidth=1)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    #ax.set_title(r'$\mathrm{Histogram\ of\ IQ:}\ \mu=100,\ \sigma=15$')
    # ax.set_xlim(40, 160)
    # ax.set_ylim(0, 0.03)
    ax.grid(grid_show)
    figfi = open(figname,'wb')
    plt.savefig(figfi,dpi= resolution,format='pdf')
    figfi.close()
    plt.close()
    

def mplscatterplot(valuelis,figname='defaulscatterplotname.pdf',xlabel='xaxis',ylabel='yaxis',resolution=150,grid_show=False):
    x = [float(ele[0]) for ele in valuelis]
    y = [float(ele[1]) for ele in valuelis]
    
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(x, y, c='b', marker='o', cmap=None, norm=None,
            vmin=0.0, vmax=None, alpha=None, linewidths=None,
            verts=None)

    #ticks = arange(-0.06, 0.061, 0.02)
    #xticks(ticks)
    #yticks(ticks)

    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True)
    

    
    figfi = open(figname,'wb')
    fig.savefig(figfi,dpi= resolution,format='pdf')
    figfi.close()
    
    






def mplscatterhist(valuelis,figname='defaulscatterhistogramtplotname.pdf',xlabel='xaxis',ylabel='yaxis',resolution=150,grid_show=False):


    # the random data
    x = [ele[0] for ele in valuelis]
    y = [ele[1] for ele in valuelis]

    # # the random data
    # x = np.random.randn(1000)
    # y = np.random.randn(1000)


    fig = plt.figure()


    # the scatter plot:
    axScatter = fig.add_subplot(111)
    # axScatter = plt.subplot(111)
    axScatter.scatter(x, y)
    axScatter.set_aspect(1.)
    
    # create new axes on the right and on the top of the current axes
    # The first argument of the new_vertical(new_horizontal) method is
    # the height (width) of the axes to be created in inches.
    divider = make_axes_locatable(axScatter)
    axHistx = divider.append_axes("top", 1.2, pad=0.1, sharex=axScatter)
    axHisty = divider.append_axes("right", 1.2, pad=0.1, sharey=axScatter)
    
    # make some labels invisible
    plt.setp(axHistx.get_xticklabels() + axHisty.get_yticklabels(),
             visible=False)
    
    # now determine nice limits by hand:
    # binwidth = 0.25
    # xymax = np.max( [np.max(np.fabs(x)), np.max(np.fabs(y))] )
    # lim = ( int(xymax/binwidth) + 1) * binwidth
    # 
    # bins = np.arange(-lim, lim + binwidth, binwidth)
    n, bins, patches = plt.hist(valuelis,  normed=1, facecolor='green', alpha=0.75)
    axHistx.hist(x, bins=bins)
    axHisty.hist(y, bins=bins, orientation='horizontal')
    
    # the xaxis of axHistx and yaxis of axHisty are shared with axScatter,
    # thus there is no need to manually adjust the xlim and ylim of these
    # axis.
    
    #axHistx.axis["bottom"].major_ticklabels.set_visible(False)
    for tl in axHistx.get_xticklabels():
        tl.set_visible(False)
    axHistx.set_yticks([0, 50, 100])
    
    #axHisty.axis["left"].major_ticklabels.set_visible(False)
    for tl in axHisty.get_yticklabels():
        tl.set_visible(False)
    axHisty.set_xticks([0, 50, 100])
    # 
    # plt.draw()
    # plt.show()
    figfi = open(figname,'wb')
    fig.savefig(figfi,dpi= resolution,format='pdf')
    figfi.close()
    plt.close()
    fig.close()

# mu, sigma = 100, 15
# x = mu + sigma * np.random.randn(10000)
# histogram_plot(x,90)




def getcolor(sigcat):
    sigcat2color={}
    majorcolors=['#0000A0', '#0000FF', '#008500', '#00CC00', '#00FF00',
     '#00FFFF', '#269926', '#39E639', '#408080', '#67E667',
     '#800000', '#800080', '#804000', '#808000', '#85004B',
     '#992667', '#A60000', '#A64B00', '#BF3030', '#BF7130',
     '#CD0074', '#E6399B', '#E667AF', '#FF0000', '#FF0000',
     '#FF0080', '#FF00FF', '#FF4040', '#FF7373', '#FF7400',
     '#FF8040', '#FF9640', '#FFB273', '#FFFF00']
    
    for idx in sigcat:
        if idx in sigcat2color:
            continue

        else:
            col=random.choice(majorcolors)
            majorcolors.remove(col)
        sigcat2color[idx]=col
    return sigcat2color



def newind(ind,width):
    nind=[]
    for ele in ind:
        nele=ele+width
        nind.append(nele)
    return nind
    
    
def plot_SI(data,labels, finam, maxval):
    N=len(labels)
    serlabels=tuple([ele[2] for ele in data])
    fig = plt.figure(figsize=(20,10))
    fig.subplots_adjust(left=0.2)
    ax = fig.add_subplot(111)
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    if maxval:
        ax.set_ylim(top=maxval)
    ind = np.arange(N)  # the x locations for the groups
    width = 0.2 # the width of the bars

    tind=np.arange(N)
    series=[]
    sigcat=[ele[2] for ele in data]
    sc2color= getcolor(sigcat)
    for mean,stdev,slabel in data:
        splot = ax.bar(tind, mean, width, color=sc2color[slabel], yerr=stdev)
        tind=newind(tind,width)
        series.append(splot[0])

    # # add some
    ax.set_ylabel('Signal')
    ax.set_xticks(ind+width)
    ax.set_xticklabels( labels)
    fig.autofmt_xdate()
    # fig.legend(ser,ccolor,loc='right',shadow=False)
    series=tuple(series)
    ax.legend( series,serlabels,loc='best',shadow=False )
    figout=open(finam,'w')
    plt.savefig(figout,format='pdf')
    figout.close()





