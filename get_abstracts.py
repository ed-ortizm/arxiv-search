"""
Filter abstracts from arXiv emails and save them to a PDF file.
The filtering is according to the keywords specified in the
configuration file.
The keywords correspond to the categories of interest for my research.
"""

import configparser
import imaplib
import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas

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
mail = imaplib.IMAP4_SSL('imap.gmail.com')

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

print(f"Succesful read: {result}")

# Get the list of email IDs
email_ids = data[0]
# Split the email IDs into a list
email_ids = email_ids.split()

# Create the PDF file
save_to = config.get('pdf', 'save_to')

pdf_file = 'results.pdf'
canvas = Canvas(pdf_file, pagesize=letter)

# Set the font and font size
canvas.setFont('Helvetica', 12)

# Loop through the email IDs and retrieve the emails
for idx, email_id in enumerate(email_ids):

    fetch_result, data = mail.fetch(email_id, "(RFC822)")
    email = data[0][1]

    # Convert the email to a string
    email = email.decode('utf-8')

    print(email)

    if idx == 0:
        break

    # if '[Message clipped]  View entire message' in email:
    #     # Extract the link to the full message from the email
    #     soup = BeautifulSoup(email, 'html.parser')
    #     view_link = soup.find('a')['href']

    #     # Send a GET request to the link to retrieve the full message
    #     r = requests.get(view_link, timeout=5)

    #     # Parse the response
    #     soup = BeautifulSoup(r.text, 'html.parser')

    #     # Get the titles and abstracts from the response
    #     titles = soup.find_all('div', {'class': 'list-title'})
    #     abstracts = soup.find_all('blockquote', {'class': 'abstract mathjax'})

    # else:
    #     soup = BeautifulSoup(email, 'html.parser')
    #     titles = soup.find_all('div', {'class': 'list-title'})
    #     abstracts = soup.find_all('blockquote', {'class': 'abstract mathjax'})

    # print(abstracts, titles)

    # # Loop through the titles and abstracts
    # for title, abstract in zip(titles, abstracts):
    #     # Check if any of the keywords are in the title or abstract
    #     if any(
    #         keyword in title.text
    #         or
    #         keyword in abstract.text
    #         for keyword in keywords
    #     ):
    #         # Add the title and abstract to the PDF file
    #         canvas.drawString(50, 750, title.text)
    #         canvas.drawString(50, 730, abstract.text)
    #         canvas.showPage()

    # # Save the PDF file
    # canvas.save()

    # # Disconnect from the email server
    # mail.close()
    # mail.logout()
