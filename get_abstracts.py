"""
Filter abstracts from arXiv emails and save them to a PDF file.
The filtering is according to the keywords specified in the
configuration file.
The keywords correspond to the categories of interest for my research.
"""

import configparser
import imaplib
import re
import requests
from bs4 import BeautifulSoup


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

        # Check if the email is clipped and get the full message
        if '[Message clipped]  View entire message' in email_body:

            # Extract the link to the full message from the email
            soup = BeautifulSoup(email_body, 'html.parser')
            view_link = soup.find('a')['href']

            # Send a GET request to the link to retrieve the full message
            r = requests.get(view_link, timeout=5)

            # Parse the response
            soup = BeautifulSoup(r.text, 'html.parser')

            # update email_body as the full message text without html
            email_body = soup.text

        matches = re.findall(
            r'[Tt]itle:(.*?)-{5,}',
            email_body,
            re.DOTALL
        )

        # select elements with the keywords in the matches
        relevant_matches = []

        for idx, match in enumerate(matches):

            if any(keyword in match for keyword in keywords):

                print(f"Match {idx}", end="\r")

                relevant_matches.append(match)

save_to = config.get('pdf', 'save_to')

with open(f"{save_to}/results.txt", "w", encoding='utf-8') as f:

    for match in relevant_matches:

        f.write(match)