import os
import re
import datetime
from pathlib import Path
import win32com.client

# ---------------- Configurable Settings ---------------- #
LOOKBACK_HOURS = 24  # Time window to look back for emails
SUBJECT_REGEX = r"Important Report ID: (\d+)"  # Adjust this to match the actual subject format
SAVE_EMAIL_DIR = Path("C:/Temp/SavedEmails")  # Directory to save matched emails
TEMP_ATTACHMENT_DIR = Path("C:/Temp/Attachments")  # Directory to store temporary attachments

SAVE_EMAIL_DIR.mkdir(parents=True, exist_ok=True)
TEMP_ATTACHMENT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------- Helper Functions ---------------- #
def extract_info_from_subject(subject: str) -> str:
    # Try to extract specific info from the subject using regex
    match = re.search(SUBJECT_REGEX, subject)
    return match.group(1) if match else None

def save_attachments(mail_item, target_folder: Path):
    # Save all attachments to the specified folder
    saved_files = []
    for attachment in mail_item.Attachments:
        path = target_folder / attachment.FileName
        attachment.SaveAsFile(str(path))
        saved_files.append(path)
    return saved_files

def save_email_as_msg(mail_item, output_folder: Path):
    # Save the email as a .msg file using a safe file name
    timestamp = mail_item.ReceivedTime.strftime("%Y%m%d_%H%M%S")
    safe_subject = re.sub(r"[^\w\s-]", "", mail_item.Subject)[:50].strip()
    filename = f"{timestamp}_{safe_subject}.msg"
    mail_item.SaveAs(str(output_folder / filename), 3)  # 3 = olMsg format

# ---------------- Main Processing Logic ---------------- #
def process_mailbox():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    inbox = outlook.GetDefaultFolder(6)  # 6 = Inbox
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # Sort by received time (latest first)

    lookback_time = datetime.datetime.now() - datetime.timedelta(hours=LOOKBACK_HOURS)

    for message in messages:
        try:
            if message.Class != 43:  # Only process MailItem objects
                continue

            if message.ReceivedTime < lookback_time:
                break  # Stop once we're past the lookback window

            subject = message.Subject or ""
            info = extract_info_from_subject(subject)

            if info:
                print(f"✓ Match: {subject} | From: {message.SenderName}")
                save_email_as_msg(message, SAVE_EMAIL_DIR)
                saved_files = save_attachments(message, TEMP_ATTACHMENT_DIR)

                # Placeholder for future attachment parsing logic
                # parse_attachment(saved_files)

            else:
                print(f"↪ Subject fallback: {subject}")

        except Exception as e:
            print(f"⚠️ Error handling message: {e}")

# ---------------- Run ---------------- #
if __name__ == "__main__":
    process_mailbox()
