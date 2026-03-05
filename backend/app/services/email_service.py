"""
Personal AI Command Center - Email Integration Service
"""
import imaplib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header
from typing import List, Optional
import asyncio
from datetime import datetime

from app.core.config import settings


class EmailService:
    """Email integration service using IMAP/SMTP"""
    
    def __init__(self):
        self.imap_server = settings.IMAP_SERVER
        self.imap_port = settings.IMAP_PORT
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.email_address = settings.EMAIL_ADDRESS
        self.email_password = settings.EMAIL_PASSWORD
        self.imap_connection = None
        self.smtp_connection = None
    
    async def connect_imap(self) -> bool:
        """Connect to IMAP server"""
        try:
            self.imap_connection = imaplib.IMAP4_SSL(
                self.imap_server,
                self.imap_port
            )
            self.imap_connection.login(
                self.email_address,
                self.email_password
            )
            return True
        except Exception as e:
            print(f"IMAP connection error: {e}")
            return False
    
    async def connect_smtp(self) -> bool:
        """Connect to SMTP server"""
        try:
            self.smtp_connection = smtplib.SMTP(
                self.smtp_server,
                self.smtp_port
            )
            self.smtp_connection.starttls()
            self.smtp_connection.login(
                self.email_address,
                self.email_password
            )
            return True
        except Exception as e:
            print(f"SMTP connection error: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from servers"""
        if self.imap_connection:
            try:
                self.imap_connection.close()
                self.imap_connection.logout()
            except:
                pass
        
        if self.smtp_connection:
            try:
                self.smtp_connection.quit()
            except:
                pass
    
    async def list_emails(
        self,
        folder: str = "INBOX",
        limit: int = 50,
        unread_only: bool = False
    ) -> List[dict]:
        """List emails from folder"""
        if not self.imap_connection:
            await self.connect_imap()
        
        emails = []
        
        try:
            # Select folder
            self.imap_connection.select(folder)
            
            # Search for emails
            if unread_only:
                status, messages = self.imap_connection.search(None, "UNSEEN")
            else:
                status, messages = self.imap_connection.search(None, "ALL")
            
            if status != "OK":
                return emails
            
            # Get email IDs
            email_ids = messages[0].split()
            
            # Limit results
            email_ids = email_ids[-limit:] if len(email_ids) > limit else email_ids
            
            for email_id in email_ids:
                # Fetch email
                status, msg_data = self.imap_connection.fetch(
                    email_id,
                    "(RFC822)"
                )
                
                if status != "OK":
                    continue
                
                # Parse email
                import email
                from email.utils import parseaddr
                
                msg = email.message_from_bytes(msg_data[0][1])
                
                # Decode subject
                subject = msg.get("Subject", "")
                decoded_subject = []
                for part, encoding in decode_header(subject):
                    if isinstance(part, bytes):
                        part = part.decode(encoding or "utf-8", errors="ignore")
                    decoded_subject.append(part)
                subject = "".join(decoded_subject)
                
                # Get sender
                sender = parseaddr(msg.get("From", ""))[1]
                
                # Get date
                date_str = msg.get("Date", "")
                
                # Get body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            try:
                                body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                                break
                            except:
                                pass
                else:
                    try:
                        body = msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                    except:
                        pass
                
                emails.append({
                    "id": email_id.decode(),
                    "sender": sender,
                    "subject": subject,
                    "body": body[:500],  # Limit body length
                    "date": date_str,
                    "read": not unread_only
                })
            
            return emails
            
        except Exception as e:
            print(f"Error listing emails: {e}")
            return emails
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> bool:
        """Send an email"""
        if not self.smtp_connection:
            await self.connect_smtp()
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.email_address
            msg["To"] = to
            msg["Subject"] = subject
            
            # Add body
            if html:
                msg.attach(MIMEText(body, "html"))
            else:
                msg.attach(MIMEText(body, "plain"))
            
            # Send
            self.smtp_connection.sendmail(
                self.email_address,
                to,
                msg.as_string()
            )
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    async def classify_email(self, email: dict) -> str:
        """Classify email using local LLM (Ollama)"""
        try:
            import ollama
            
            # Prepare prompt
            prompt = f"""Classify the following email into one of these categories:
- important
- notification
- promotion
- social
- spam

Email from: {email.get('sender', '')}
Subject: {email.get('subject', '')}
Body: {email.get('body', '')[:200]}

Reply with only the category name."""

            # Call Ollama
            response = ollama.chat(
                model=settings.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            category = response.get("message", {}).get("content", "").strip().lower()
            
            # Validate category
            valid_categories = ["important", "notification", "promotion", "social", "spam"]
            if category not in valid_categories:
                category = "notification"
            
            return category
            
        except Exception as e:
            print(f"Error classifying email: {e}")
            return "notification"
    
    async def generate_reply(self, email: dict) -> str:
        """Generate reply using local LLM (Ollama)"""
        try:
            import ollama
            
            # Prepare prompt
            prompt = f"""Generate a brief, professional reply to the following email:

From: {email.get('sender', '')}
Subject: {email.get('subject', '')}
Body: {email.get('body', '')[:500]}

Reply:"""

            # Call Ollama
            response = ollama.chat(
                model=settings.DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.get("message", {}).get("content", "").strip()
            
        except Exception as e:
            print(f"Error generating reply: {e}")
            return "Thank you for your email. I will get back to you soon."


# Create instance
email_service = EmailService()
