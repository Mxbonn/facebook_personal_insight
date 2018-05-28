# Gain insights from your personal facebook data.

With GDPR becoming active on 25/05/2018, facebook released a tool to download all your personal data.
The data can be downloaded on facebook.com **settings -> Your Facebook information -> Download your information**.
The resulting folder structure looks like this:
```
── data_root
   ├── about_you
   ├── ads
   ├── apps
   ├── calls_and_messages
   ├── comments
   ├── events
   ├── following_and_followers
   ├── friends
   ├── groups
   ├── likes_and_reactions
   ├── location_history
   ├── marketplace
   ├── messages
   ├── network_information
   ├── other_activity
   ├── pages
   ├── payment_history
   ├── photos
   ├── posts
   ├── profile_information
   ├── saved_items
   ├── search_history
   ├── security_and_login_information
   ├── videos
   └── your_places

```

This project contains tools to gather analysis from your **messages** and **likes and reactions**.
Use `parser.py` to create csv files that need to be present for the analysis functions to work.

-----
Blog post with more information:
https://medium.com/@mxbonn/i-analysed-my-own-facebook-data-b6b74958e1c0
