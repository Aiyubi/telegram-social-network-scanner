# telegram-social-network-scanner

A python project that uses a telegram userbot to scan a start channel and all channels within messages. The scaned information can be displayed as social media graph.

# Motivation
In recent years, german media often labeled the messenger telegram as a place for conspiracy believers. A quick look showed a huge amount of groups that are all connected by forwarding each others messages or linking in other ways to one another.

This projects aim is NOT to be political, but display size/followers/connections of this social network to get a better view on the situation.

The idea is to start at one or more channels, and then get all the connections automatically without any need for the human to do anything. 

Display of the data is currently WIP.

While this tool was designed with a specific group in mind, it is designed to work with any channel given.

# Usage

1. install requirements

    `python -m pip install -r requirements.txt`

2. copy and edit the config file

    `cp config.py.example config.py`
    `nano config.py`

    For this you will need a telegram API application. You can create those [here](https://core.telegram.org/api/obtaining_api_id). I recommend not using your regular telegram account, as you might hit daily limits during the processing, which might be problematic for regular use of telegram.

    If you don't want to use the filebased sqlite database, you can use other relational databases as described  [here](https://docs.sqlalchemy.org/en/13/core/engines.html)

    Start channels can be delivered in 3 foramts: @telegam_username , the http links, or if you are a member of the channel you can also use its ID.

3. execute the database file to initialize the database structure

    `python utils/database.py`

4. You can now execute the scanning for channels

    `python scan.py`
    
    This might take several days to scan, depending on the scale of your network.
    
5. (WIP) visualize the result

    `python visualize.py`

# Technical notes
## structure
The general concept for data flow can be seen in this picture:

![Draft of dataflow](https://i.imgur.com/j2kermA.jpg)

To be included in a scan, a chat needs to meet the following criteria:
* be a channel, this includes supergroups, but not users or bots 
* be public visible (no joining the channel required)
* have a username set

## limits
Userbots in telegram have the same limitations as users. For this project this will mainly be the amounts of profiles loaded. Once a user hits that limits, no new profiles can be called. The way telethon works, profiles loaded by  ID from scaned messages, do not count. This is why there are 2 queues for scaned entitys:
* `queue_links_forward` for forwards. These messages get processed when async decides to do so.
* `queue_links_text` for text entities. These will count towards the limit and will only get processed if there are no more chats waiting to be processed. This way the chance to know to know the chats from forwards increase.

# Issues
Feel free to submit issues and enhancement requests.

# Contribution
Feel free to create pull requests through github. Plase make sure you are using the latest commit to do so.

# License
This project is published under the BSD 3-Clause License. (see License file for details)
