"""
Filter abstracts from arXiv emails and save them to a PDF file.
The filtering is according to the keywords specified in the
configuration file.
The keywords correspond to the categories of interest for my research.
"""

import configparser
import datetime
import imaplib
import re


# read config file
config = configparser.ConfigParser(
    interpolation=configparser.ExtendedInterpolation()
)

config.read('get_abstracts.ini')

# Get:
# email, password, and keywords

my_email = config.get('email', 'email')
password = config.get('email', 'password')

keywords = config.get('email', 'keywords').split(',')
keywords = [keyword.strip() for keyword in keywords]

# Connect to the email server

with imaplib.IMAP4_SSL('imap.gmail.com') as mail:

    # Log in to the email account
    mail.login(my_email, password)

    # Select the mailbox you want to search
    mail.select('INBOX')

    # Search the specified pattern
    result, data = mail.search(
        None,
        'ALL',
        'FROM "no-reply@arxiv.org"'
    )

    # Get the list of email IDs
    email_ids = data[0]

    # Split the email IDs into a list
    email_ids = email_ids.split()

    print(f"Succesful read: {result}. Found {len(email_ids)} emails.\n")

    # Loop through the email IDs and retrieve the emails

    for idx, email_id in enumerate(email_ids):

        fetch_result, data = mail.fetch(email_id, "(RFC822)")
        email_body = data[0][1].decode("utf-8")

        # save the email body to a file
        with open(
            f"/home/edgar/Downloads/{idx}.txt",
            "w",
            encoding='utf-8'
        ) as f:

            f.write(email_body)

        matches = re.findall(
            r'[Tt]itle:(.*?)-{5,}',
            email_body,
            re.DOTALL
        )

        # select elements with the keywords in the matches
        relevant_matches = []

        for idx, match in enumerate(matches):

            if any(keyword in match for keyword in keywords):

                # print(f"Match {idx}", end="\r")

                relevant_matches.append(match)

# get time stamp to add to the file name

now = datetime.datetime.now()
time_stamp = now.strftime("%Y-%m-%d_%H-%M-%S")


save_to = config.get('directory', 'save_to')
file_name = config.get('file', 'file_name')

with open(
    f"{save_to}/abstracts_{time_stamp}.txt", "w", encoding='utf-8'
) as f:

    for match in relevant_matches:

        f.write(match)
