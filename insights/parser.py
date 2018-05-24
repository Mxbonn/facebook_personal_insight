import csv
import os
import re

from bs4 import BeautifulSoup

def likes_and_reactions(data_path):
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

def messages(data_path, conversation):
    path = os.path.join(data_path, "messages")
    path = os.path.join(path, conversation)
    messages_html_path = os.path.join(path, "message.html")
    print("Loading html source ...")
    soup = BeautifulSoup(open(messages_html_path), "html.parser")
    csv_path = os.path.join(path, "message.csv")
    print("Writing csv ...")
    with open(csv_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=",")
        header = ['time', 'sender']
        writer.writerow(header)
        for message_div in soup.select('div[role="main"] > div.pam._3-95._2pi0._2lej.uiBoxWhite.noborder'):
            sender = message_div.find("div", "_3-96 _2pio _2lek _2lel").get_text()
            time_text = message_div.find("div", "_3-94 _2lem").get_text()
            writer.writerow([time_text, sender])
