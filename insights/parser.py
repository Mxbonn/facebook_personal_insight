import argparse
import csv
import os
import re

from bs4 import BeautifulSoup

def likes_and_reactions(data_path):
    """
    Parse likes_and_reactions/posts_and_comments.html to a csv file that can be used
    in the processing functions.

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.

    """
    path = os.path.join(data_path, "likes_and_reactions/")
    html_path = os.path.join(path, "posts_and_comments.html")
    soup = BeautifulSoup(open(html_path), "html.parser")
    csv_path = os.path.join(path, "posts_and_comments.csv")

    reg_1 = re.compile(r"^(.*?)(?: like(?:s|d) | reacted to )(.*?)(?:'s| own)")
    reg_2 = re.compile(r"(\w+)\.png")
    with open(csv_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        header = ['time', 'reaction', 'liker', 'poster']
        writer.writerow(header)
        for reaction_div in soup.find_all("div", "pam _3-95 _2pi0 _2lej uiBoxWhite noborder"):
            reaction_text = reaction_div.find("div", "_3-96 _2pio _2lek _2lel").get_text()
            liker = reg_1.match(reaction_text).group(1)
            poster = reg_1.match(reaction_text).group(2)
            full_reaction = reaction_div.find("div", "_2pin").find("img")['src']
            reaction = reg_2.search(full_reaction).group(1)
            time = reaction_div.find("div", "_3-94 _2lem").get_text()
            writer.writerow([time, reaction, liker, poster])

def messages(data_path):
    """
    Parse message from conversation to a csv file that can be used
    in the processing functions.

    Parameters
    ----------
    data_path : str
        Path to the root directory of your personal facebook data.
    """
    path = os.path.join(data_path, "messages/inbox")

    conversations = os.listdir(path)
    for conversation in conversations:
        conversation_path = os.path.join(path, conversation)
        messages_html_path = os.path.join(conversation_path, "message.html")
        if os.path.isfile(messages_html_path):
            print(conversation)
            print("Loading html source ...")
            soup = BeautifulSoup(open(messages_html_path), "html.parser")
            csv_path = os.path.join(conversation_path, "message.csv")
            print("Writing csv ...")
            with open(csv_path, 'w') as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                header = ['time', 'sender', 'text']
                writer.writerow(header)
                for message_div in soup.select('div[role="main"] > div.pam._3-95._2pi0._2lej.uiBoxWhite.noborder'):
                    sender_div = message_div.find("div", "_3-96 _2pio _2lek _2lel")
                    if sender_div:
                        sender = sender_div.get_text()
                    else:
                        sender = "unknown"
                    time_text = message_div.find("div", "_3-94 _2lem").get_text()
                    text_div =  message_div.select('div._3-96._2let > div > div')
                    if len(text_div) > 1:
                        text = text_div[1].get_text()
                    else:
                        text = "unknown"
                    writer.writerow([time_text, sender, text])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('path', type=str,
                        help='path to the root directory of the downloaded Facebook data.')
    args = parser.parse_args()
    messages(args.path)