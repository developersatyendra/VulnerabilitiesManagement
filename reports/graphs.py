from matplotlib import pyplot
import math
import numpy
from io import BytesIO
import base64


LINE_WIDTH = 1
OPACITY = 0.9
# Bar Constant
BAR_WIDTH = 0.4
# PIE Constant
PIE_EXPLODE = 0.05
# Red, Yellow, Green, Blue
COLORS = ['#bf0404', '#df7416', '#fdfc25', '#4B98FF', '#ff9999', '#66b3ff', '#99ff99', '#ffcc99',]
COLORS_GRADIENT = ['#4B98FF', '#3F80D6', '#366EB8', '#2D5C99', '#28528A', '#24497A', '#214370', '#172F4F', '#12253D', '#0D1B2E', '#08111C', '#04090F', '#03060A']


# Render Bar Char
# labely = Main label of Y
# labelx = Main label of X


def RenderBarChart(data=[], labels=[], labely='', labelx=''):

    # Save render image to ByteIO instead of file
    image = BytesIO()

    # Create Y tick values
    maxyValue = int(math.ceil(max(data) / 10.0)) * 10
    if 30 <= maxyValue <50:
        horizonStep = 5
    elif int(math.ceil(max(data) / 10.0)) * 10 < 30:
        horizonStep = 2
    else:
        horizonStep = 10

    yInt = range(0, int(math.ceil(max(data) / 10.0)) * 10 + 1, horizonStep)
    fig, ax = pyplot.subplots()
    pyplot.yticks(yInt)

    # Add more horizontal dash lines
    for i in yInt:
        ax.axhline(y=i, linestyle='--', dashes=(2, 1), linewidth=0.5, alpha=0.4, color='black', zorder=0)

    # Render bar chart
    y_pos = numpy.arange(len(labels))

    ax.bar(y_pos, data, BAR_WIDTH, color=COLORS, alpha=OPACITY, edgecolor=COLORS, linewidth=LINE_WIDTH, zorder=3)
    pyplot.xticks(y_pos, labels)
    pyplot.xlabel(labelx)
    pyplot.ylabel(labely)
    fig.set_size_inches(6, 4)
    pyplot.tight_layout()
    pyplot.savefig(image, format='png', bbox_inches='tight')
    pyplot.clf()
    pyplot.close(fig)
    return '<img src="data:image/png;base64,{}"/>'.format(base64.b64encode(image.getvalue()).decode())


# Render Donut Chart
def RenderDonutChart(data=[], labels=[], size=100):
    sumData = sum(data)
    for index, data_t in enumerate(data):
        labels[index] = '{0:.1f}'.format(data_t*100./sumData) + '% ' +labels[index]
    image = BytesIO()
    fig, ax = pyplot.subplots(figsize=(6, 3), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=-120, pctdistance=0.84, colors=COLORS_GRADIENT)
    kw = dict(xycoords='data', textcoords='data', arrowprops=dict(arrowstyle="-"), zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        if p.theta2-p.theta1 < 3:
            continue
        y = numpy.sin(numpy.deg2rad(ang))
        x = numpy.cos(numpy.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(numpy.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(labels[i], xy=(x, y), xytext=(1.15*numpy.sign(x), 1.5*y), horizontalalignment=horizontalalignment, fontsize=9, **kw)

    fig.set_size_inches(6, 4)
    pyplot.tight_layout()
    pyplot.savefig(image, box_inches='tight', pad_inches=0.0)
    pyplot.clf()
    pyplot.close(fig)
    return '<img style="width: {}%" src="data:image/png;base64, {}">'.format(size ,base64.b64encode(image.getvalue()).decode())


# Render Stack Bar Chart
# labely = Main label of Y
# labelx = Main label of X
# xticks = Labels of bars

def RenderStackBarChart(data, labels=[], labely='', labelx='', xticks=[]):

    # Save Image to ByteIO instead of File
    image = BytesIO()
    # the x locations for the bars
    ind = numpy.arange(len(data[0]))

    # Title Legend Array
    titleLegend = []

    # Total each column
    sumValue = None

    fig, ax = pyplot.subplots()
    # Process all bars in data set
    for index, data_t in enumerate(data):
        if index == 0:
            sumValue = numpy.array(data_t)
        else:
            sumValue = sumValue + numpy.array(data_t)
        bottom = numpy.array([])
        for i in range(index):
            if len(bottom) != 0:
                bottom = bottom + numpy.array(data[i])
            else:
                bottom = numpy.array(data[i])
        if len(bottom) !=0:
            p1 = ax.bar(ind, data_t, BAR_WIDTH, bottom=bottom, color=COLORS[3-index], alpha=OPACITY, zorder=3)
        else:
            p1 = ax.bar(ind, data_t, BAR_WIDTH, color=COLORS[3-index], alpha=OPACITY, zorder=3)
        titleLegend.append(p1)

    # Reverse
    titleLegend = titleLegend[::-1]
    if max(sumValue) < 20:
        horizonStep = 2
    elif max(sumValue) <40:
        horizonStep = 5
    elif max(sumValue) <100:
        horizonStep = 10
    else:
        horizonStep = 50
    # Add more horizontal dash lines
    for i in range(0, max(sumValue) + horizonStep, horizonStep):
        ax.axhline(y=i, linestyle='--', dashes=(2, 1), linewidth=0.5, alpha=0.4, color='black', zorder=0)

    ax.set_xlim(-0.47, len(data[0]) - 1 + 0.47)
    pyplot.ylabel(labely)
    pyplot.xlabel(labelx)
    pyplot.xticks(ind, xticks, rotation=60, fontsize=8)
    pyplot.yticks(numpy.arange(0, max(sumValue) + horizonStep + 1, horizonStep))
    pyplot.legend(titleLegend, labels, loc='upper right', bbox_to_anchor=(1, 1))
    pyplot.tight_layout()
    pyplot.savefig(image)
    pyplot.clf()
    pyplot.close(fig)
    return '<img src="data:image/png;base64, {}">'.format(base64.b64encode(image.getvalue()).decode())


if __name__ == '__main__':

    data = [1, 1, 18, 20, 20, 9]
    tags = ['HTTPS', 'HTTP', 'SSH', 'NetBios', 'FTP', 'VNC']
    strRet = RenderBarChart(data, tags, labely='Vulnerabilities') + RenderDonutChart(data, tags)
    print(strRet)

    data_t = [[1, 2, 50, 15, 24], [2, 15, 27, 11, 9], [9, 1, 2, 3, 5], [10, 11, 12, 13, 55]]
    B = ['scan_1', 'scan_2', 'scan_3', 'scan_4', 'scan_5']
    A = ['High', 'Medium', 'Low', 'Information']
    print(RenderStackBarChart(data_t, labels=A, xticks=B, labely='Vulnerabilities'))
