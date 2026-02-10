# app/services/email_service.py
import os
from typing import List, Optional
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, HtmlContent
from sqlmodel import Session, select
from app.db import engine
from app.models import Subscriber
from app.pipeline.fetchers import fetch_sport_sample
from app.pipeline.llm import compose_fact
from app.pipeline.agents import render_blurb

# Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "facts@sportsfacts.app")
FROM_NAME = os.getenv("FROM_NAME", "Sports Facts")

class EmailService:
    def __init__(self):
        self.sg = None
        if SENDGRID_API_KEY and not SENDGRID_API_KEY.startswith("YOUR_"):
            self.sg = SendGridAPIClient(SENDGRID_API_KEY)
    
    def is_configured(self) -> bool:
        """Check if SendGrid is properly configured."""
        return self.sg is not None
    
    async def generate_daily_fact(self, sport: str = "random") -> dict:
        """Generate a fact for the daily email."""
        try:
            # Fetch data
            fields = await fetch_sport_sample(sport)
            
            # Try LLM first, fallback to template
            llm_fact = compose_fact(fields)
            fact_text = llm_fact if llm_fact else render_blurb(fields)
            
            return {
                "text": fact_text,
                "sport": fields.get("sport", sport),
                "llm_used": bool(llm_fact),
                "data": fields
            }
        except Exception as e:
            print(f"Error generating fact: {e}")
            return {
                "text": "Did you know? Sports bring people together from all around the world!",
                "sport": sport,
                "llm_used": False,
                "data": {}
            }
    
    def create_email_html(self, fact: dict, subscriber_email: str) -> str:
        """Create HTML email content."""
        sport = fact.get("sport", "sports").upper()
        fact_text = fact.get("text", "")
        
        emoji = "🏀" if sport == "NBA" else "⚾" if sport == "MLB" else "🏆"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your Daily Sports Fact</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background-color: white;
                    border-radius: 12px;
                    padding: 40px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 20px;
                }}
                .logo {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #2563eb;
                    margin-bottom: 10px;
                }}
                .fact-box {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    margin: 30px 0;
                    text-align: center;
                    font-size: 20px;
                }}
                .sport-badge {{
                    display: inline-block;
                    background-color: rgba(255,255,255,0.2);
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-size: 14px;
                    margin-top: 15px;
                }}
                .cta {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .cta-button {{
                    display: inline-block;
                    background-color: #2563eb;
                    color: white;
                    padding: 12px 30px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #eee;
                    color: #666;
                    font-size: 12px;
                }}
                .footer a {{
                    color: #2563eb;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🏆 Sports Facts</div>
                    <p style="color: #666; margin: 0;">Your daily dose of sports trivia</p>
                </div>
                
                <h2 style="text-align: center; color: #333;">Your Fact of the Day</h2>
                
                <div class="fact-box">
                    <div style="font-size: 48px; margin-bottom: 15px;">{emoji}</div>
                    <p style="margin: 0; font-weight: 500;">{fact_text}</p>
                    <div class="sport-badge">{sport}</div>
                </div>
                
                <div class="cta">
                    <p style="color: #666; margin-bottom: 15px;">Want more amazing facts?</p>
                    <a href="https://sportsfacts.app" class="cta-button">Generate Another Fact</a>
                </div>
                
                <div class="footer">
                    <p>You're receiving this because you subscribed to Sports Facts daily emails.</p>
                    <p>
                        <a href="https://sportsfacts.app/unsubscribe?email={subscriber_email}">Unsubscribe</a> | 
                        <a href="https://sportsfacts.app">Visit Website</a>
                    </p>
                    <p style="margin-top: 20px; color: #999;">
                        © 2024 Sports Facts. All rights reserved.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    async def send_email(self, to_email: str, fact: dict) -> bool:
        """Send a single email with the daily fact."""
        if not self.is_configured():
            print(f"SendGrid not configured. Would send to {to_email}")
            print(f"Fact: {fact.get('text', '')}")
            return False
        
        try:
            html_content = self.create_email_html(fact, to_email)
            
            message = Mail(
                from_email=Email(FROM_EMAIL, FROM_NAME),
                to_emails=To(to_email),
                subject=f"🏆 Your Daily Sports Fact - {fact.get('sport', 'Sports').upper()}",
                html_content=html_content
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent successfully to {to_email}")
                return True
            else:
                print(f"❌ Failed to send email to {to_email}: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending email to {to_email}: {e}")
            return False
    
    async def send_daily_emails(self, sport: str = "random") -> dict:
        """Send daily emails to all subscribers."""
        # Generate fact
        fact = await self.generate_daily_fact(sport)
        
        with Session(engine) as session:
            # Get all subscribers
            subscribers = session.exec(select(Subscriber)).all()
            
            sent_count = 0
            failed_count = 0
            
            for subscriber in subscribers:
                # Check if subscriber wants this sport
                if sport == "random":
                    # For random, pick based on subscriber preferences
                    if subscriber.nba and not subscriber.mlb:
                        subscriber_sport = "nba"
                    elif subscriber.mlb and not subscriber.nba:
                        subscriber_sport = "mlb"
                    else:
                        # Has both or none, use random
                        subscriber_sport = "random"
                else:
                    subscriber_sport = sport
                
                # Generate fact for this subscriber if needed
                if subscriber_sport != sport:
                    subscriber_fact = await self.generate_daily_fact(subscriber_sport)
                else:
                    subscriber_fact = fact
                
                # Send email
                success = await self.send_email(subscriber.email, subscriber_fact)
                if success:
                    sent_count += 1
                else:
                    failed_count += 1
            
            return {
                "total": len(subscribers),
                "sent": sent_count,
                "failed": failed_count,
                "fact": fact
            }

# Singleton instance
email_service = EmailService()
