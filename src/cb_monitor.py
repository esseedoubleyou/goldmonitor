"""
Tier 2 Data Monitor: Hybrid Central Bank Activity

This module automates DETECTION of new WGC reports but requires manual EXTRACTION.

Why hybrid?
- Central bank data updates quarterly (45-60 day lag)
- Published in PDFs with inconsistent layouts
- Automating PDF extraction is fragile and high-maintenance
- Manual extraction takes <5 minutes per quarter
- This is a structural signal, not time-critical

Workflow:
1. Script checks WGC website for new quarterly reports
2. If found, sends notification (email/terminal)
3. Human downloads PDF, extracts net CB purchases (one number)
4. Human runs manual_cb_update.py to append to CSV
5. Monthly report reads from CSV
"""

import json
import re
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


class CentralBankMonitor:
    """
    Hybrid system for central bank data:
    - Automates detection of new WGC reports
    - Prompts manual extraction
    - Reads from manually-maintained CSV
    """
    
    STATE_FILE = Path('data/cb_monitor_state.json')
    DATA_FILE = Path('data/cb_reserves.csv')
    WGC_URL = "https://www.gold.org/goldhub/research/gold-demand-trends"
    
    def __init__(self, email_config: Optional[Dict] = None):
        """
        Initialize monitor.
        
        Args:
            email_config: Optional dict with email settings (from, to, smtp_server, etc.)
        """
        self.email_config = email_config
        self.STATE_FILE.parent.mkdir(exist_ok=True)
        self.load_state()
    
    def load_state(self):
        """Load previously-checked quarters from state file."""
        try:
            with open(self.STATE_FILE, 'r') as f:
                self.state = json.load(f)
        except FileNotFoundError:
            self.state = {'checked_quarters': [], 'last_check': None}
    
    def save_state(self):
        """Persist state to disk."""
        self.state['last_check'] = datetime.now().isoformat()
        with open(self.STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def check_for_new_report(self) -> Optional[str]:
        """
        Scrape WGC reports page for new quarterly publications.
        
        Returns:
            Quarter string (e.g., 'Q3_2025') if new report found, None otherwise
        """
        print(f"\n📡 Checking WGC website for new reports...")
        print(f"   URL: {self.WGC_URL}")
        
        try:
            response = requests.get(self.WGC_URL, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find report links (WGC uses various formats)
            # Look for links containing "gold demand trends" and quarter patterns
            reports = soup.find_all('a', href=re.compile(r'gold-demand-trends', re.I))
            
            found_quarters = []
            
            for report in reports[:5]:  # Check 5 most recent links
                text = report.get_text()
                
                # Match patterns like "Q3 2025", "Q1-2025", "Q4'24"
                match = re.search(r'Q([1-4])[\s\-\']+(\d{2,4})', text, re.I)
                
                if match:
                    quarter_num = match.group(1)
                    year = match.group(2)
                    
                    # Normalize year (handle 2-digit years)
                    if len(year) == 2:
                        year = f"20{year}"
                    
                    quarter = f"Q{quarter_num}_{year}"
                    found_quarters.append((quarter, report))
            
            # Check if any are new
            for quarter, report_link in found_quarters:
                if quarter not in self.state['checked_quarters']:
                    # New report found!
                    print(f"✅ New WGC report detected: {quarter}")
                    
                    self.state['checked_quarters'].append(quarter)
                    self.save_state()
                    
                    # Get PDF URL
                    pdf_url = report_link.get('href', '')
                    if pdf_url and not pdf_url.startswith('http'):
                        pdf_url = f"https://www.gold.org{pdf_url}"
                    
                    # Send notification
                    self._notify_new_report(quarter, pdf_url)
                    
                    return quarter
            
            print(f"   No new reports. Last checked quarters: {self.state['checked_quarters'][-3:]}")
            return None
            
        except requests.RequestException as e:
            print(f"⚠️  Error checking WGC website: {e}")
            return None
        except Exception as e:
            print(f"⚠️  Unexpected error: {e}")
            return None
    
    def _notify_new_report(self, quarter: str, pdf_url: str):
        """
        Send notification about new report.
        Tries email first (if configured), falls back to terminal.
        """
        message = self._format_notification(quarter, pdf_url)
        
        # Always print to terminal
        print(message)
        
        # Try email if configured
        if self.email_config and self.email_config.get('enabled'):
            try:
                self._send_email(
                    subject=f"🚨 New WGC Gold Report: {quarter}",
                    body=message
                )
                print(f"✅ Email notification sent to {self.email_config['to']}")
            except Exception as e:
                print(f"⚠️  Email notification failed: {e}")
    
    def _format_notification(self, quarter: str, pdf_url: str) -> str:
        """Generate instructions for manual data extraction."""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║  🚨 NEW WGC GOLD DEMAND TRENDS REPORT DETECTED               ║
╚══════════════════════════════════════════════════════════════╝

Quarter: {quarter}
Report: {pdf_url}

MANUAL ACTION REQUIRED:
1. Download the PDF report from the URL above
2. Find the "Central Banks & Other Institutions" row in the demand table
   (Usually on pages 10-15, in "Gold demand by sector" section)
3. Record the NET tonnes purchased for the quarter
4. Run: python scripts/manual_cb_update.py
   Or manually update: {self.DATA_FILE}

Expected CSV format:
quarter,cb_net_tonnes,source,validated_date
{quarter},<tonnes>,WGC,{datetime.now().date()}

Example:
{quarter},287,WGC,{datetime.now().date()}

This should take < 5 minutes. The monthly report will use this data.

╚══════════════════════════════════════════════════════════════╝
"""
    
    def _send_email(self, subject: str, body: str):
        """Send email notification using SMTP."""
        msg = MIMEMultipart()
        msg['From'] = self.email_config['from']
        msg['To'] = self.email_config['to']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(
            self.email_config['smtp_server'], 
            self.email_config['smtp_port']
        )
        server.starttls()
        server.login(self.email_config['from'], self.email_config['password'])
        server.send_message(msg)
        server.quit()
    
    def get_latest_data(self) -> Dict:
        """
        Read latest CB data from manually-maintained CSV.
        
        Returns:
            Dict with data + freshness warnings
        """
        try:
            if not self.DATA_FILE.exists():
                return {
                    'error': 'CB data file not found',
                    'status': 'missing',
                    'message': f'Run: python scripts/manual_cb_update.py --init'
                }
            
            df = pd.read_csv(self.DATA_FILE)
            
            if df.empty:
                return {
                    'error': 'CB data file is empty',
                    'status': 'empty'
                }
            
            df['validated_date'] = pd.to_datetime(df['validated_date'])
            
            latest = df.iloc[-1]
            days_old = (datetime.now() - latest['validated_date']).days
            
            return {
                'quarter': latest['quarter'],
                'cb_net_tonnes': float(latest['cb_net_tonnes']),
                'source': latest['source'],
                'validated_date': latest['validated_date'],
                'days_old': days_old,
                'is_stale': days_old > 90,
                'status': 'stale' if days_old > 90 else 'current',
                'all_quarters': df.to_dict('records')  # Include history
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'error'
            }
    
    def initialize_csv(self, sample_data: bool = True):
        """
        Create initial CB reserves CSV.
        
        Args:
            sample_data: If True, populate with sample historical data
        """
        self.DATA_FILE.parent.mkdir(exist_ok=True)
        
        if sample_data:
            # Sample data from recent WGC reports
            # User should replace with actual data
            data = pd.DataFrame({
                'quarter': ['Q3_2024', 'Q4_2024'],
                'cb_net_tonnes': [333.0, 290.0],  # Example values
                'source': ['WGC', 'WGC'],
                'validated_date': ['2024-11-15', '2025-02-20']
            })
        else:
            # Empty structure
            data = pd.DataFrame(columns=['quarter', 'cb_net_tonnes', 'source', 'validated_date'])
        
        data.to_csv(self.DATA_FILE, index=False)
        print(f"✅ Initialized {self.DATA_FILE}")
        
        if sample_data:
            print(f"⚠️  Sample data included - update with actual WGC figures!")


def test_monitor():
    """Test function to check WGC scraping."""
    from dotenv import load_dotenv
    load_dotenv()
    
    # Setup email config if provided
    email_config = None
    if os.getenv('EMAIL_ENABLED', 'false').lower() == 'true':
        email_config = {
            'enabled': True,
            'from': os.getenv('EMAIL_FROM'),
            'to': os.getenv('EMAIL_TO'),
            'smtp_server': os.getenv('EMAIL_SMTP_SERVER'),
            'smtp_port': int(os.getenv('EMAIL_SMTP_PORT', 587)),
            'password': os.getenv('EMAIL_PASSWORD')
        }
    
    monitor = CentralBankMonitor(email_config)
    
    # Check for new reports
    new_report = monitor.check_for_new_report()
    
    # Check current data status
    data = monitor.get_latest_data()
    print(f"\nCurrent CB data status:")
    print(f"  Status: {data.get('status')}")
    
    if data.get('status') == 'current' or data.get('status') == 'stale':
        print(f"  Quarter: {data.get('quarter')}")
        print(f"  Net tonnes: {data.get('cb_net_tonnes')}")
        print(f"  Days old: {data.get('days_old')}")


if __name__ == "__main__":
    test_monitor()

