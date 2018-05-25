import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd


def like_statistics(data_path, top=20, yearly=False, fixed_top=False, show=False):
    """

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.
    top : int or None, default 20
        Number of unique friends/pages you liked posts from.
        if None all liked posts are analysed.
    yearly : bool or tuple(start_year, end_year) , default False
        if bool, determines if the amount of likes should be analysed per year or globally.
        if tuple, tuple of the first and last year of the range to analyse.
    fixed_top : bool
        Used when yearly is not False.
        Determines if the top liked friends/pages should be stay fixed for all years or
        only be calculated for each year individually.
    show : bool, default to False
        Show the generated plot.


    Notes
    -----
    When plotting yearly data, top cannot be False.

    """
    likes_path = os.path.join(data_path, "likes_and_reactions")
    csv_path = os.path.join(likes_path, "posts_and_comments.csv")
    df = pd.read_csv(csv_path)
    df['time'] = pd.to_datetime(df['time'], format="%d %B %Y %H:%M")
    df = df.sort_values('time')
    df['date'] = df['time'].dt.date
    end_year = df['date'].max().year
    start_year = df['date'].min().year
    if isinstance(yearly, tuple):
        start_year = yearly[0]
        end_year = yearly[1]
    rows = end_year - start_year + 1
    start_date = datetime.date(start_year,1,1)
    end_date = datetime.date(end_year,12, 31)
    df = df[(df['date'] > start_date) & (df['date'] < end_date)]
    index = df.poster.value_counts().head(top).index

    if yearly:
        if top is not None:
            x_length = top * 1
            fig, axes = plt.subplots(rows, 1, figsize=(x_length, 6 * rows))
            fig.subplots_adjust(hspace=1)
            for r in range(rows):
                ax = axes[r]
                df_year = df[df['time'].dt.year == start_year + r]
                if fixed_top:
                    df_year.poster.value_counts().head(top).reindex(index, fill_value=0).plot(kind='bar', ax=ax,
                                                            alpha=0.7)
                else:
                    df_year.poster.value_counts().head(top).plot(kind='bar', ax=ax,
                                                            alpha=0.7)
                ax.yaxis.grid(linestyle=':', alpha=0.6)
                ax.set_title(start_year + r)
        else:
            raise ValueError("Yearly=true and top=None cannot be combined.")
    else:
        if top is not None:
            x_length = top * 1
            fig, ax = plt.subplots(1,1, figsize=(x_length ,5))
            df.poster.value_counts().head(top).plot(kind='bar', alpha=0.7)
        else:
            x_length = len(df.poster.value_counts()) * 0.3
            fig, ax = plt.subplots(1,1, figsize=(x_length ,5))
            df.poster.value_counts().plot(kind='bar', alpha=0.7)
        ax.yaxis.grid(linestyle=':', alpha=0.6)


    output_path = os.path.join(likes_path, "insights")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    file_name =  "likes_statistics.png"
    file_name = os.path.join(output_path, file_name)
    plt.savefig(file_name, bbox_inches='tight')

    if show:
        plt.show()
    plt.close()