import datetime
import os

from insights.utils import m2hm
from matplotlib.dates import DayLocator, DateFormatter
from matplotlib.ticker import FuncFormatter, MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


COLORS = ['#5DADE2', '#EB984E', '#48C9B0', '#F4D03F', '#AF7AC5', '#EC7063', '#45B39D', '#CACFD2']
EDGE_COLORS = ['#2874A6', '#AF601A', '#148F77', '#B7950B', '#76448A', '#B03A2E', '#117A65', '#839192']

def plot_messages(data_path, conversation, tick_width=1, days=365, show=False):
    messages_path = os.path.join(data_path, "messages")
    path = os.path.join(messages_path, conversation)
    csv_path = os.path.join(path, "message.csv")

    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df = df.sort_values('time')
    df['date'] = df['time'].dt.date
    df['minutes'] = df['time'].dt.hour * 60 + df['time'].dt.minute

    end_date = df['date'].max()
    start_date = max(df['date'].min(), end_date - datetime.timedelta(days))
    df = df[df['date'] >= start_date]
    start_date = max(df['date'].min(), end_date - datetime.timedelta(days))

    senders = df['sender'].unique()

    if df.shape[0] <= 1 or start_date == end_date:
        return

    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i, sender in enumerate(senders):
        i = i % len(COLORS)
        df_sender = df[df['sender'] == sender]
        ax.plot_date(df_sender['date'], df_sender['minutes'], color=COLORS[i], markeredgecolor=EDGE_COLORS[i],
                     alpha=0.5, label=sender)

    major_locator = MultipleLocator(60)
    minor_locator = MultipleLocator(10)
    ax.set_ylim(0, 1440)
    ax.yaxis.set_major_locator(major_locator)
    ax.yaxis.set_minor_locator(minor_locator)
    ax.yaxis.set_major_formatter(FuncFormatter(m2hm))
    y_length = tick_width * 24 * 6
    y_length = max(y_length, 10)
    ax.yaxis.grid(linestyle=':', linewidth=0.5)

    ax.xaxis.set_major_locator(DayLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))
    ax.xaxis.grid(linestyle=':', linewidth=0.5)
    start_date = df['date'].min()
    end_date = df['date'].max()
    period = (end_date - start_date).days
    x_length = period * tick_width
    x_length = max(x_length, 5)
    fig.set_size_inches(x_length, y_length)
    fig.autofmt_xdate(rotation=90)
    ax.legend()

    output_path = os.path.join(messages_path, "insights")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name = conversation + "_messages.png"
    file_name = os.path.join(output_path, file_name)
    plt.savefig(file_name, bbox_inches='tight')
    if show:
        plt.show()
    plt.close()
    return


def plot_amount_messages(data_path, conversation, tick_width=1, days=365, show=False):
    messages_path = os.path.join(data_path, "messages")
    path = os.path.join(messages_path, conversation)
    csv_path = os.path.join(path, "message.csv")

    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df = df.sort_values('time')
    df['date'] = df['time'].dt.normalize()
    df['minutes'] = df['time'].dt.hour * 60 + df['time'].dt.minute
    df = df.groupby(['date', 'sender']).size().reset_index(name='amount_messages')

    end_date = df['date'].max()
    start_date = max(df['date'].min(), end_date - datetime.timedelta(days))
    df = df[df['date'] >= start_date]
    date_range = pd.date_range(start_date, end_date, freq="1D")

    senders = df['sender'].unique()

    index = pd.MultiIndex.from_product([date_range, senders],
                                       names=["date", "sender"])
    df.set_index(['date', 'sender'], drop=True, inplace=True)
    df = df.reindex(index, fill_value=0)
    df.reset_index(inplace=True)
    if df.shape[0] <= 1:
        return

    fig = plt.figure()
    ax = fig.add_subplot(111)
    for i, sender in enumerate(senders):
        i = i % len(COLORS)
        df_sender = df[df['sender'] == sender]
        dates = df_sender['date'].tolist()
        if i == 0:
            ax.bar(dates, df_sender['amount_messages'], color=COLORS[i],
                   alpha=0.8, label=sender)
            bottom = np.array(df_sender['amount_messages'].tolist())
        else:
            ax.bar(dates, df_sender['amount_messages'], color=COLORS[i], bottom=bottom,
                   alpha=0.8, label=sender)
            bottom += np.array(df_sender['amount_messages'].tolist())

        for x, y, value in zip(dates, bottom, df_sender['amount_messages']):
            if value != 0:
                ax.text(x, y + 1, str(value))

    ax.xaxis_date()

    major_locator = MultipleLocator(10)
    ax.yaxis.set_major_locator(major_locator)
    ax.yaxis.grid(linestyle=':', linewidth=0.5)
    y_length = max(ax.get_ylim()[1] / 10 * tick_width, 10)

    ax.xaxis.set_major_locator(DayLocator())
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))
    ax.xaxis.grid(linestyle=':', linewidth=0.5)
    period = (end_date - start_date).days
    x_length = max(period * tick_width, 5)
    fig.autofmt_xdate(rotation=90)
    fig.set_size_inches(x_length, y_length)
    plt.title("Amount messages per day.")
    ax.legend()

    output_path = os.path.join(messages_path, "insights")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name = conversation + "_amount_messages.png"
    file_name = os.path.join(output_path, file_name)
    plt.savefig(file_name, bbox_inches='tight')

    if show:
        plt.show()
    plt.close()
