"""
Enhanced Stock-Notion Integration with Public APIs
Uses Yahoo Finance public API for stock data that works on any hosting platform
"""

import requests
from notion_client import Client
from datetime import datetime, date
import argparse
import time
import json

class ImprovedStockNotionIntegrator:
    def __init__(self, notion_token: str, stock_database_id: str, portfolio_database_id: str):
        """
        Initialize the Enhanced Stock-Notion integrator with portfolio tracking
        
        Args:
            notion_token (str): Notion integration token
            stock_database_id (str): Main stock database ID
            portfolio_database_id (str): Historical portfolio database ID
        """
        self.notion = Client(auth=notion_token)
        self.stock_database_id = stock_database_id
        self.portfolio_database_id = portfolio_database_id
        
        # Default stock symbols to track
        self.default_stocks = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'AMD', 'NFLX']
        
    def fetch_stock_data(self, symbol: str):
        """
        Fetch stock data from Yahoo Finance public API
        
        Args:
            symbol (str): Stock symbol to fetch
            
        Returns:
            dict: Stock data dictionary or None if failed
        """
        try:
            print(f"Fetching data for {symbol}...")
            
            # Use Yahoo Finance public API endpoints
            # Method 1: Try Yahoo Finance query API
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'region': 'US',
                'lang': 'en-US',
                'includePrePost': 'false',
                'interval': '1d',
                'range': '5d',
                'corsDomain': 'finance.yahoo.com',
                '.tsrc': 'finance'
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"API request failed for {symbol}: {response.status_code}")
                return None
                
            data = response.json()
            
            if not data or 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                print(f"No data found for {symbol}")
                return None
                
            result = data['chart']['result'][0]
            meta = result['meta']
            
            # Get current price
            current_price = meta.get('regularMarketPrice', 0)
            if current_price == 0:
                current_price = meta.get('previousClose', 0)
            
            # Get company name - try multiple sources
            company_name = meta.get('longName', meta.get('shortName', symbol))
            
            # Calculate previous close from historical data
            previous_close = 0
            
            # Method 1: Try to get from historical closes
            if 'indicators' in result and 'quote' in result['indicators']:
                quotes = result['indicators']['quote'][0]
                closes = [x for x in quotes.get('close', []) if x is not None and x > 0]
                
                if len(closes) >= 2:
                    # Use the second-to-last close as previous close
                    previous_close = closes[-2]
                elif len(closes) >= 1:
                    # If only one close available, check meta for previous close
                    if 'chartPreviousClose' in meta and meta['chartPreviousClose'] > 0:
                        previous_close = meta['chartPreviousClose']
                    else:
                        # Use current price as fallback
                        previous_close = current_price
            
            # Method 2: Try meta fields if historical data didn't work
            if previous_close == 0:
                if 'previousClose' in meta and meta['previousClose'] > 0:
                    previous_close = meta['previousClose']
                elif 'chartPreviousClose' in meta and meta['chartPreviousClose'] > 0:
                    previous_close = meta['chartPreviousClose']
                else:
                    # Final fallback to current price
                    previous_close = current_price
            
            # Get other data with fallbacks
            volume = meta.get('regularMarketVolume', meta.get('volume', 0))
            market_cap = meta.get('marketCap', 0)
            fifty_two_week_high = meta.get('fiftyTwoWeekHigh', 0)
            fifty_two_week_low = meta.get('fiftyTwoWeekLow', 0)
            
            # Calculate changes
            price_change = current_price - previous_close if previous_close > 0 else 0
            percent_change = (price_change / previous_close * 100) if previous_close > 0 else 0
            
            stock_data = {
                'symbol': symbol,
                'company_name': company_name,
                'current_price': current_price,
                'previous_close': previous_close,
                'price_change': price_change,
                'percent_change': percent_change,
                'volume': volume,
                'market_cap': market_cap,
                'fifty_two_week_high': fifty_two_week_high,
                'fifty_two_week_low': fifty_two_week_low,
                'exchange': meta.get('exchangeName', meta.get('fullExchangeName', 'Unknown')),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            print(f"✅ {symbol}: ${current_price:.2f} (Previous: ${previous_close:.2f}, Change: ${price_change:+.2f})")
            return stock_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error fetching data for {symbol}: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {str(e)}")
            return None
    
    def get_stocks_from_database(self):
        """
        Dynamically get all stock symbols from the Notion database
        
        Returns:
            List of stock symbols currently in the database
        """
        try:
            print("🔍 Scanning Notion database for stocks...")
            
            # Query the database to get all pages
            response = self.notion.databases.query(
                database_id=self.stock_database_id,
                page_size=100  # Adjust if you have more than 100 stocks
            )
            
            stocks = []
            for page in response['results']:
                # Extract stock symbol from the title property
                title_property = page['properties'].get('Stock Symbol', {})
                if 'title' in title_property and title_property['title']:
                    symbol = title_property['title'][0]['text']['content']
                    stocks.append(symbol)
            
            print(f"✅ Found {len(stocks)} stocks in database: {', '.join(stocks)}")
            return stocks
            
        except Exception as e:
            print(f"❌ Error getting stocks from database: {str(e)}")
            print("🔄 Falling back to default stock list...")
            return self.default_stocks
    
    def find_stock_page(self, symbol: str):
        """
        Find existing stock page in Notion database
        
        Args:
            symbol (str): Stock symbol to find
            
        Returns:
            str: Page ID if found, None otherwise
        """
        try:
            response = self.notion.databases.query(
                database_id=self.stock_database_id,
                filter={
                    "property": "Stock Symbol",
                    "title": {
                        "equals": symbol
                    }
                }
            )
            
            if response['results']:
                return response['results'][0]['id']
            return None
            
        except Exception as e:
            print(f"Error finding stock page for {symbol}: {str(e)}")
            return None
    
    def update_stock_in_notion(self, stock_data: dict):
        """
        Update or create stock entry in Notion database
        
        Args:
            stock_data (dict): Stock data dictionary
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            symbol = stock_data['symbol']
            
            # Find existing page
            page_id = self.find_stock_page(symbol)
            
            # Prepare properties using correct property names from user's database
            properties = {
                "Stock Symbol": {
                    "title": [
                        {
                            "text": {
                                "content": symbol
                            }
                        }
                    ]
                },
                "Company Name": {
                    "rich_text": [
                        {
                            "text": {
                                "content": stock_data['company_name']
                            }
                        }
                    ]
                },
                "Current Price": {
                    "number": stock_data['current_price']
                },
                "Prev Close": {
                    "number": stock_data['previous_close']
                },
                "Price Change": {
                    "number": stock_data['price_change']
                },
                "Change Percentage": {
                    "number": stock_data['percent_change']
                },
                "Volume": {
                    "number": stock_data['volume']
                },
                "Market Cap": {
                    "number": stock_data['market_cap']
                },
                "52-Week High/Low": {
                    "rich_text": [
                        {
                            "text": {
                                "content": f"${stock_data['fifty_two_week_high']:.2f} / ${stock_data['fifty_two_week_low']:.2f}"
                            }
                        }
                    ]
                },
                "Exchange": {
                    "select": {
                        "name": stock_data['exchange']
                    }
                },
                "Last Updated": {
                    "date": {
                        "start": datetime.now().strftime('%Y-%m-%d')
                    }
                }
            }
            
            if page_id:
                # Update existing page
                self.notion.pages.update(
                    page_id=page_id,
                    properties=properties
                )
                print(f"✅ Updated {symbol} in Notion")
            else:
                # Create new page
                self.notion.pages.create(
                    parent={"database_id": self.stock_database_id},
                    properties=properties
                )
                print(f"✅ Created new entry for {symbol} in Notion")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating {symbol} in Notion: {str(e)}")
            return False
    
    def update_stocks(self, symbols=None):
        """
        Update stock prices for given symbols or all stocks in database
        
        Args:
            symbols (list): List of symbols to update, or None for all stocks
        """
        if symbols is None:
            # Get all stocks from database dynamically
            symbols = self.get_stocks_from_database()
        
        print(f"🔄 Updating {len(symbols)} stocks...")
        
        updated_count = 0
        failed_count = 0
        
        for symbol in symbols:
            stock_data = self.fetch_stock_data(symbol)
            if stock_data:
                success = self.update_stock_in_notion(stock_data)
                if success:
                    updated_count += 1
                else:
                    failed_count += 1
            else:
                failed_count += 1
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        print(f"\n📊 Update Summary:")
        print(f"   ✅ Successfully updated: {updated_count}")
        print(f"   ❌ Failed to update: {failed_count}")
        
        return updated_count, failed_count
    
    def add_stock(self, symbol: str):
        """
        Add a new stock to tracking with automatic historical integration
        
        Args:
            symbol (str): Stock symbol to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"➕ Adding {symbol} to tracking system...")
            
            # Fetch current stock data
            stock_data = self.fetch_stock_data(symbol)
            if not stock_data:
                print(f"❌ Failed to fetch data for {symbol}")
                return False
            
            # Add to main database
            success = self.update_stock_in_notion(stock_data)
            if not success:
                print(f"❌ Failed to add {symbol} to main database")
                return False
            
            # Add to portfolio database for historical tracking (if portfolio database exists)
            if self.portfolio_database_id:
                try:
                    portfolio_properties = {
                        "Stock Symbol": {
                            "title": [
                                {
                                    "text": {
                                        "content": symbol
                                    }
                                }
                            ]
                        },
                        "Date": {
                            "date": {
                                "start": datetime.now().strftime('%Y-%m-%d')
                            }
                        },
                        "Price": {
                            "number": stock_data['current_price']
                        },
                        "Shares Owned": {
                            "number": 0  # Default to 0, user can update
                        },
                        "Total Value": {
                            "number": 0  # Will be calculated when shares are added
                        }
                    }
                    
                    self.notion.pages.create(
                        parent={"database_id": self.portfolio_database_id},
                        properties=portfolio_properties
                    )
                    print(f"✅ Added {symbol} to portfolio tracking")
                    
                except Exception as e:
                    print(f"⚠️ Added to main database but failed to add to portfolio: {str(e)}")
            
            print(f"🎉 Successfully added {symbol} with automatic integration!")
            return True
            
        except Exception as e:
            print(f"❌ Error adding {symbol}: {str(e)}")
            return False
    
    def get_portfolio_summary(self):
        """
        Get portfolio summary with current values
        
        Returns:
            dict: Portfolio summary data
        """
        try:
            print("📊 Calculating portfolio summary...")
            
            if not self.portfolio_database_id:
                # If no portfolio database, try to get portfolio data from main database
                return self.get_portfolio_summary_from_main_db()
            
            # Get all portfolio entries
            response = self.notion.databases.query(
                database_id=self.portfolio_database_id,
                page_size=100
            )
            
            total_value = 0
            total_investment = 0
            positions = 0
            
            for page in response['results']:
                properties = page['properties']
                
                # Get stock symbol
                symbol_prop = properties.get('Stock Symbol', {})
                if not symbol_prop.get('title'):
                    continue
                    
                symbol = symbol_prop['title'][0]['text']['content']
                
                # Get shares owned and purchase price
                shares = properties.get('Shares Owned', {}).get('number', 0) or 0
                purchase_price = properties.get('Purchase Price', {}).get('number', 0) or 0
                
                if shares > 0 and purchase_price > 0:
                    positions += 1
                    
                    # Get current price from main database
                    current_price = self.get_current_price(symbol)
                    if current_price > 0:
                        current_value = shares * current_price
                        investment_value = shares * purchase_price
                        
                        total_value += current_value
                        total_investment += investment_value
            
            gain_loss = total_value - total_investment
            return_pct = (gain_loss / total_investment * 100) if total_investment > 0 else 0
            
            return {
                'total_value': total_value,
                'total_investment': total_investment,
                'gain_loss': gain_loss,
                'return_percentage': return_pct,
                'positions': positions
            }
            
        except Exception as e:
            print(f"❌ Error calculating portfolio summary: {str(e)}")
            return {
                'total_value': 0,
                'total_investment': 0,
                'gain_loss': 0,
                'return_percentage': 0,
                'positions': 0
            }
    
    def get_portfolio_summary_from_main_db(self):
        """
        Get portfolio summary from main database if no separate portfolio database
        """
        try:
            response = self.notion.databases.query(
                database_id=self.stock_database_id,
                page_size=100
            )
            
            total_value = 0
            total_investment = 0
            positions = 0
            
            for page in response['results']:
                properties = page['properties']
                
                # Get shares owned and purchase price from main database
                shares = properties.get('Shares Owned', {}).get('number', 0) or 0
                purchase_price = properties.get('Purchase Price', {}).get('number', 0) or 0
                current_price = properties.get('Current Price', {}).get('number', 0) or 0
                
                if shares > 0 and purchase_price > 0 and current_price > 0:
                    positions += 1
                    current_value = shares * current_price
                    investment_value = shares * purchase_price
                    
                    total_value += current_value
                    total_investment += investment_value
            
            gain_loss = total_value - total_investment
            return_pct = (gain_loss / total_investment * 100) if total_investment > 0 else 0
            
            return {
                'total_value': total_value,
                'total_investment': total_investment,
                'gain_loss': gain_loss,
                'return_percentage': return_pct,
                'positions': positions
            }
            
        except Exception as e:
            print(f"❌ Error calculating portfolio summary from main DB: {str(e)}")
            return {
                'total_value': 0,
                'total_investment': 0,
                'gain_loss': 0,
                'return_percentage': 0,
                'positions': 0
            }
    
    def get_current_price(self, symbol: str):
        """
        Get current price for a symbol from the main database
        
        Args:
            symbol (str): Stock symbol
            
        Returns:
            float: Current price or 0 if not found
        """
        try:
            response = self.notion.databases.query(
                database_id=self.stock_database_id,
                filter={
                    "property": "Stock Symbol",
                    "title": {
                        "equals": symbol
                    }
                }
            )
            
            if response['results']:
                properties = response['results'][0]['properties']
                return properties.get('Current Price', {}).get('number', 0) or 0
            
            return 0
            
        except Exception as e:
            print(f"Error getting current price for {symbol}: {str(e)}")
            return 0
    
    def create_portfolio_snapshot(self):
        """
        Create a daily portfolio snapshot for historical tracking
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print("📸 Creating portfolio snapshot...")
            
            if not self.portfolio_database_id:
                print("⚠️ No portfolio database configured for snapshots")
                return False
            
            summary = self.get_portfolio_summary()
            
            # Create snapshot entry
            snapshot_properties = {
                "Date": {
                    "title": [
                        {
                            "text": {
                                "content": datetime.now().strftime('%Y-%m-%d')
                            }
                        }
                    ]
                },
                "Total Value": {
                    "number": summary['total_value']
                },
                "Total Investment": {
                    "number": summary['total_investment']
                },
                "Gain/Loss": {
                    "number": summary['gain_loss']
                },
                "Return %": {
                    "number": summary['return_percentage']
                },
                "Positions": {
                    "number": summary['positions']
                }
            }
            
            self.notion.pages.create(
                parent={"database_id": self.portfolio_database_id},
                properties=snapshot_properties
            )
            
            print(f"✅ Created portfolio snapshot: ${summary['total_value']:.2f} total value")
            return True
            
        except Exception as e:
            print(f"❌ Error creating portfolio snapshot: {str(e)}")
            return False

if __name__ == "__main__":
    # Configuration
    NOTION_TOKEN = "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"
    STOCK_DATABASE_ID = "24fe1ee2ae7a80438c24d1c79249b1d7"
    PORTFOLIO_DATABASE_ID = "24fe1ee2ae7a800eadfccdb682641562"
    
    # Initialize integrator
    integrator = ImprovedStockNotionIntegrator(
        NOTION_TOKEN, 
        STOCK_DATABASE_ID, 
        PORTFOLIO_DATABASE_ID
    )
    
    # Command line interface
    parser = argparse.ArgumentParser(description='Enhanced Stock-Notion Integration')
    parser.add_argument('action', choices=['update', 'add', 'portfolio', 'snapshot'], 
                       help='Action to perform')
    parser.add_argument('symbol', nargs='?', help='Stock symbol (for add action)')
    parser.add_argument('--symbols', nargs='+', help='Specific symbols to update')
    
    args = parser.parse_args()
    
    if args.action == 'update':
        integrator.update_stocks(args.symbols)
    elif args.action == 'add':
        if args.symbol:
            integrator.add_stock(args.symbol.upper())
        else:
            print("❌ Please provide a stock symbol to add")
    elif args.action == 'portfolio':
        summary = integrator.get_portfolio_summary()
        print(f"\n💰 Portfolio Summary:")
        print(f"   Total Value: ${summary['total_value']:,.2f}")
        print(f"   Total Investment: ${summary['total_investment']:,.2f}")
        print(f"   Gain/Loss: ${summary['gain_loss']:+,.2f}")
        print(f"   Return: {summary['return_percentage']:+.2f}%")
        print(f"   Positions: {summary['positions']}")
    elif args.action == 'snapshot':
        integrator.create_portfolio_snapshot()

