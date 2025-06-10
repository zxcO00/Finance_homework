import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

def CandlePlot(ax, Data, colorup='r', colordown='g'):
    time = Data['time']
    openp = Data['open']
    high = Data['high']
    low = Data['low']
    close = Data['close']

    width = 0.6
    width2 = 0.1

    for i in range(len(time)):
        if close[i] >= openp[i]:
            color = colorup
            lower = openp[i]
            height = close[i] - openp[i]
        else:
            color = colordown
            lower = close[i]
            height = openp[i] - close[i]

        # 畫實體蠟燭
        ax.add_patch(plt.Rectangle((i - width/2, lower), width, height, color=color))

        # 畫上下影線
        ax.vlines(i, low[i], high[i], color=color, linewidth=1)

    ax.set_xlim(-1, len(time))
    ax.set_xticks(range(len(time)))
    ax.set_xticklabels([t.strftime('%Y-%m-%d') for t in time], rotation=45, ha='right')
    ax.set_title("K 線圖")
    ax.grid(True)
