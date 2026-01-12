import os
from notion_client import Client
from typing import Optional, Dict, Any
from datetime import datetime

class NotionManager:
    """
    A class to manage interactions with the Notion API.
    """

    def __init__(self, token: str, database_id: str):
        """
        Initialize the NotionManager with API credentials.

        Args:
            token (str): Notion integration token.
            database_id (str): The ID of the Notion database.
        """
        if not token or not database_id:
            raise ValueError("Notion Token and Database ID must be provided.")
            
        self.client = Client(auth=token)
        self.database_id = database_id

    def add_stock_record(self, 
                         ticker: str, 
                         price: float, 
                         summary: str, 
                         date: Optional[str] = None,
                         status: str = "Analyzed") -> Optional[Dict[str, Any]]:
        """
        Adds a new page to the Notion database with stock details.

        Args:
            ticker (str): The stock ticker symbol.
            price (float): The current stock price.
            summary (str): AI-generated summary or notes.
            date (Optional[str]): The date of the record (ISO 8601 format). Defaults to current time.
            status (str): The status tag for the record.

        Returns:
            Optional[Dict[str, Any]]: The response from the Notion API if successful, None otherwise.
        """
        if date is None:
            date = datetime.now().isoformat()

        try:
            new_page = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties={
                    "Ticker": {
                        "title": [
                            {
                                "text": {
                                    "content": ticker
                                }
                            }
                        ]
                    },
                    "Price": {
                        "number": price
                    },
                    "Date": {
                        "date": {
                            "start": date
                        }
                    },
                    "AI_Summary": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": summary[:2000]  # Notion limit safeguard
                                }
                            }
                        ]
                    },
                    "Status": {
                        "select": {
                            "name": status
                        }
                    }
                }
            )
            return new_page
        except Exception as e:
            print(f"Error adding record to Notion: {e}")
            return None
