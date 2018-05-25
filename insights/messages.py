import datetime
import os

from insights.utils import m2hm, get_colors
from matplotlib.dates import DayLocator, DateFormatter
from matplotlib.ticker import FuncFormatter, MultipleLocator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


COLORS = ['#5DADE2', '#EB984E', '#48C9B0', '#F4D03F', '#AF7AC5', '#EC7063', '#45B39D', '#CACFD2']
EDGE_COLORS = ['#2874A6', '#AF601A', '#148F77', '#B7950B', '#76448A', '#B03A2E', '#117A65', '#839192']

def plot_messages(data_path, conversation, end_date=None, start_date=30, tick_width=1, show=False):
    """
    Plot the messages for the conversation over the specified time period.

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.
    conversation : str
        Name of the directory that contains the message.csv with all data.
    end_date : datetime-like or None, optional
        Last date to include in analysis.
    start_date : datetime-like or int, optional
        If datetime-like: first date to include in analysis.
        If int: Start date will be X days before end_date
    tick_width : float
        width in inches between consecutive ticks on both axis.
    show : bool, default to False
        Show the generated plot.
    """
    messages_path = os.path.join(data_path, "messages")
    path = os.path.join(messages_path, conversation)
    csv_path = os.path.join(path, "message.csv")

    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df = df.sort_values('time')
    df['date'] = df['time'].dt.date
    df['minutes'] = df['time'].dt.hour * 60 + df['time'].dt.minute

    last_date = df['date'].max()
    last_date = pd.Timestamp(last_date)
    if end_date is None:
        end_date = last_date
    else:
        end_date = pd.Timestamp(end_date)
        end_date = min(end_date, last_date)

    if isinstance(start_date, int):
        days = start_date
        start_date = max(pd.Timestamp(df['date'].min()), end_date - datetime.timedelta(days))
    else:
        start_date = pd.Timestamp(start_date)

    df = df[df['date'] <= end_date.date()]
    df = df[df['date'] >= start_date.date()]

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

    period = (end_date - start_date).days
    if period > 366:
        interval = 7
    else:
        interval = 1
    ax.xaxis.set_major_locator(DayLocator(interval=interval))
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))
    ax.xaxis.grid(linestyle=':', linewidth=0.5)
    x_length = period * tick_width
    x_length = max(x_length, 5)
    fig.set_size_inches(x_length, y_length)
    fig.autofmt_xdate(rotation=90)
    ax.legend()
    ax.set_title("Messages activity.")
    ax.set_xlabel("Date")
    ax.set_ylabel("Time")

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


def plot_amount_messages(data_path, conversation, end_date=None, start_date=30, tick_width=1, show=False):
    """
    Plot the amount of messages a day for the conversation over the specified time period.

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.
    conversation : str
        Name of the directory that contains the message.csv with all data.
    end_date : datetime-like or None, optional
        Last date to include in analysis.
    start_date : datetime-like or int, optional
        If datetime-like: first date to include in analysis.
        If int: Start date will be X days before end_date
    tick_width : float
        width in inches between consecutive ticks on both axis.
    show : bool, default to False
        Show the generated plot.

    """
    messages_path = os.path.join(data_path, "messages")
    path = os.path.join(messages_path, conversation)
    csv_path = os.path.join(path, "message.csv")

    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df = df.sort_values('time')
    df['date'] = df['time'].dt.normalize()
    df['minutes'] = df['time'].dt.hour * 60 + df['time'].dt.minute
    df = df.groupby(['date', 'sender']).size().reset_index(name='amount_messages')

    last_date = df['date'].max()
    if end_date is None:
        end_date = last_date
    else:
        end_date = pd.Timestamp(end_date)
        end_date = min(end_date, last_date)

    if isinstance(start_date, int):
        days = start_date
        start_date = max(df['date'].min(), end_date - datetime.timedelta(days))
    else:
        start_date = pd.Timestamp(start_date)

    df = df[df['date'] <= end_date]
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
    if df.amount_messages.max() < 40:
        offset = 0
    else:
        offset = 1
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
                ax.text(x, y + offset, str(value))

    ax.xaxis_date()

    major_locator = MultipleLocator(10)
    ax.yaxis.set_major_locator(major_locator)
    ax.yaxis.grid(linestyle=':', linewidth=0.5)
    y_length = max(ax.get_ylim()[1] / 10 * tick_width, 10)

    period = (end_date - start_date).days
    if period > 366:
        interval = 7
    else:
        interval = 1
    ax.xaxis.set_major_locator(DayLocator(interval=interval))
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))
    ax.xaxis.grid(linestyle=':', linewidth=0.5)
    x_length = max(period * tick_width, 5)
    fig.autofmt_xdate(rotation=90)
    fig.set_size_inches(x_length, y_length)
    plt.title("Amount messages per day.")
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages")

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

def message_activity_hourly(data_path, sender, show=False):
    """
    Plot activity for every hour of the day.

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.
    sender : str
        Name of the sender of the messages. Recommended to be your own name.
    show : bool, default to False
        Show the generated plot.

    """
    path = os.path.join(data_path, "messages")
    directories = os.listdir(path)
    df = None
    for directory in directories:
        directory_path = os.path.join(path, directory)
        if os.path.isdir(directory_path) and directory not in ["insights", "stickers_used"]:
            csv_path = os.path.join(directory_path, "message.csv")
            if os.path.isfile(csv_path):
                if df is None:
                    df = pd.read_csv(csv_path)
                else:
                    df = df.append(pd.read_csv(csv_path), ignore_index=True)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df = df.sort_values('time')
    df['hour'] = df['time'].dt.hour
    df = df[df['sender'] == sender]
    grouped = df.groupby(['hour']).size().reset_index(name='amount_messages')
    fig, ax = plt.subplots(1, 1, figsize=(5, 10))
    ax.barh(grouped['hour'], grouped['amount_messages'], color="#4286f4")
    major_locator = MultipleLocator(1)
    ax.yaxis.set_major_locator(major_locator)
    ax.set_ylim(-0.5, 23.5)
    ax.get_xaxis().set_visible(False)
    ax.set_title('Message activity per hour.')

    output_path = os.path.join(path, "insights")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name = "message_activity_{}.png".format(sender.replace(" ","_"))
    file_name = os.path.join(output_path, file_name)
    plt.savefig(file_name, bbox_inches='tight')

    if show:
        plt.show()
    plt.close()

def message_activity_weekly(data_path, sender, show=False):
    """
    Plot activity for every day of the week.

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.
    sender : str
        Name of the sender of the messages. Recommended to be your own name.
    show : bool, default to False
        Show the generated plot.

    """
    path = os.path.join(data_path, "messages")
    directories = os.listdir(path)
    df = None
    for directory in directories:
        directory_path = os.path.join(path, directory)
        if os.path.isdir(directory_path) and directory not in ["insights", "stickers_used"]:
            csv_path = os.path.join(directory_path, "message.csv")
            if os.path.isfile(csv_path):
                if df is None:
                    df = pd.read_csv(csv_path)
                else:
                    df = df.append(pd.read_csv(csv_path), ignore_index=True)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df = df.sort_values('time')
    df['dayofweek'] = df['time'].dt.dayofweek
    df = df[df['sender'] == sender]
    grouped = df.groupby(['dayofweek']).size().reset_index(name='amount_messages')
    fig, ax = plt.subplots(1, 1, figsize=(10, 5))
    ax.bar(grouped['dayofweek'], grouped['amount_messages'], color="#4286f4")
    major_locator = MultipleLocator(1)
    ax.yaxis.set_major_locator(major_locator)
    ax.set_xlim(-0.5, 6.5)
    ax.get_yaxis().set_visible(False)
    ax.set_title('Weekly message activity.')
    days = ['invisible tick', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    ax.set_xticklabels(days)

    output_path = os.path.join(path, "insights")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name = "message_activity_weekly_{}.png".format(sender.replace(" ","_"))
    file_name = os.path.join(output_path, file_name)
    plt.savefig(file_name, bbox_inches='tight')

    if show:
        plt.show()
    plt.close()


def most_active_chat(data_path, tick_width=1, end_date=None, start_date=30, legend="text", show=False):
    """
    Plot the most active chat for each day between start and end date.
    Dates on the X-axis, number of messages on the y-axis, and the specific chat is encoded in the color of the bars.

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.
    tick_width : float
        width in inches between consecutive ticks on both axis.
    end_date : datetime-like or None, optional
        Last date to include in analysis.
    start_date : datetime-like or int, optional
        If datetime-like: first date to include in analysis.
        If int: Start date will be X days before end_date
    legend : {"text", "box", None}
        Style for legend.
    show : bool, default to False
        Show the generated plot.

    """
    path = os.path.join(data_path, "messages")
    directories = os.listdir(path)
    df = None
    for directory in directories:
        directory_path = os.path.join(path, directory)
        if os.path.isdir(directory_path) and directory not in ["insights", "stickers_used"]:
            csv_path = os.path.join(directory_path, "message.csv")
            if os.path.isfile(csv_path):
                chat = directory.split('_')[0]
                new_df = pd.read_csv(csv_path)
                new_df['chat'] = chat
                if df is None:
                    df = new_df
                else:
                    df = df.append(new_df, ignore_index=True)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df['date'] = df['time'].dt.normalize()
    df = df.groupby(['date', 'chat']).size().reset_index(name='amount_messages')
    idx = df.groupby(['date'])['amount_messages'].transform(max) == df['amount_messages']
    df = df[idx].drop_duplicates(subset=['date', 'amount_messages'])

    last_date = df['date'].max()
    if end_date is None:
        end_date = last_date
    else:
        end_date = pd.Timestamp(end_date)
        end_date = min(end_date, last_date)

    if isinstance(start_date, int):
        days = start_date
        start_date = max(df['date'].min(), end_date - datetime.timedelta(days))
    else:
        start_date = pd.Timestamp(start_date)

    df = df[df['date'] <= end_date]
    df = df[df['date'] >= start_date]

    chats = df.chat.unique()
    colors = get_colors(len(chats))

    fig, ax = plt.subplots(1, 1)

    for i, chat in enumerate(chats):
        chat_df = df[df.chat == chat]
        ax.bar(chat_df['date'].tolist(), chat_df['amount_messages'], color=colors[i], alpha=0.8, label=chat)

    if legend == "text":
        for x, value in zip(df['date'].tolist(), df['chat']):
            ax.text(x, len(value) + ax.get_ylim()[1] / 10, value, rotation=90, size=14)
    if legend == "box":
        ax.legend()


    ax.xaxis_date()

    major_locator = MultipleLocator(10)
    ax.yaxis.set_major_locator(major_locator)
    ax.yaxis.grid(linestyle=':', linewidth=0.5)
    y_length = max(ax.get_ylim()[1] / 20 * tick_width, 10)


    period = (end_date - start_date).days
    if period > 366:
        interval = 7
    else:
        interval = 1
    ax.xaxis.set_major_locator(DayLocator(interval=interval))
    ax.xaxis.set_major_formatter(DateFormatter('%d/%m/%Y'))
    ax.xaxis.grid(linestyle=':', linewidth=0.5)
    x_length = max(period * tick_width, 5)
    fig.autofmt_xdate(rotation=90)
    fig.set_size_inches(x_length, y_length)
    ax.set_title("Most active chats.")
    ax.set_xlabel("Date")
    ax.set_ylabel("Messages")

    output_path = os.path.join(path, "insights")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name = "most_active_chat.png"
    file_name = os.path.join(output_path, file_name)
    plt.savefig(file_name, bbox_inches='tight')

    if show:
        plt.show()
    plt.close()

    return