import pandas as pd
import openai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Load API key and SMTP configuration
openai_api_key = os.getenv('OPENAI_API_KEY')
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
USERNAME = os.getenv('SMTP_USERNAME')
PASSWORD = os.getenv('SMTP_PASSWORD')

# Step 1: Load Contacts
contacts = pd.read_csv('contacts.csv')

# Step 2: Generate Email Drafts using ChatCompletion
def generate_email_draft(name, company):
    prompt = f"Write a brief and complete professional email introducing our services to {name} at {company}."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant creating short, professional email drafts."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=250
    )
    return response.choices[0].message['content'].strip()

contacts['email_draft'] = contacts.apply(
    lambda row: generate_email_draft(row['name'], row['company']),
    axis=1
)

# Save drafts for review
contacts.to_csv('draft_emails.csv', index=False)
print("Drafts generated and saved to 'draft_emails.csv'. Please review and edit as needed.")

input("Press Enter after editing 'draft_emails.csv'...")
contacts = pd.read_csv('draft_emails.csv')

# Step 3: Send Emails
def send_email(to_address, subject, body):
    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.sendmail(USERNAME, to_address, msg.as_string())

for _, row in contacts.iterrows():
    send_email(
        to_address=row['email'],
        subject=f"Message for {row['company']}",
        body=row['email_draft']
    )
    print(f"Email sent to {row['name']} at {row['company']}.")

print("All emails have been sent.")
