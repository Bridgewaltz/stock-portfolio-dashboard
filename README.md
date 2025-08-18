# 📈 Enhanced Stock-Notion Portfolio Dashboard

A professional stock portfolio tracking system that integrates with Notion databases to provide real-time stock prices, portfolio analytics, and automated data management.

## 🌟 Features

- **🔄 Real-time Stock Updates**: Live stock prices with dynamic detection
- **📊 Portfolio Tracking**: Historical performance analysis and metrics
- **📈 Daily Snapshots**: Automatic portfolio history capture
- **🎯 Easy Management**: Add stocks with automatic integration
- **💰 Portfolio Analytics**: Real-time portfolio value and performance tracking
- **🏢 Company Information**: Automatic company name and financial data fetching
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices

## 🚀 Live Demo

Visit the deployed application: [Your Railway URL will be here]

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: Notion API
- **Stock Data**: Yahoo Finance API (via Manus API Hub)
- **Hosting**: Railway
- **Styling**: Modern CSS with gradients and animations

## 📊 Dashboard Features

### Portfolio Summary
- Total portfolio value
- Total investment amount
- Gain/loss calculations
- Return percentage tracking

### Stock Management
- Add new stocks instantly
- Update all stock prices
- Dynamic stock detection from Notion
- Company name and previous close price fetching

### Historical Tracking
- Daily portfolio snapshots
- Performance over time
- Historical data export capabilities

## 🔧 Setup Instructions

### Prerequisites
- Python 3.11+
- Notion account with integration token
- Notion databases set up for stock tracking

### Local Development

1. **Clone the repository**
   ```bash
   git clone [your-repo-url]
   cd stock-portfolio-dashboard
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Update the Notion credentials in `src/main.py`:
   ```python
   NOTION_TOKEN = "your_notion_integration_token"
   STOCK_DATABASE_ID = "your_stock_database_id"
   PORTFOLIO_DATABASE_ID = "your_portfolio_database_id"  # Optional
   ```

5. **Run the application**
   ```bash
   cd src
   python main.py
   ```

6. **Access the dashboard**
   Open http://localhost:5000 in your browser

### Railway Deployment

1. **Connect to Railway**
   - Sign up at [railway.app](https://railway.app)
   - Connect your GitHub account
   - Import this repository

2. **Configure Environment Variables**
   In Railway dashboard, add:
   - `NOTION_TOKEN`: Your Notion integration token
   - `STOCK_DATABASE_ID`: Your stock database ID
   - `PORTFOLIO_DATABASE_ID`: Your portfolio database ID (optional)

3. **Deploy**
   Railway will automatically deploy your application

## 📋 Notion Database Setup

### Main Stock Database
Required properties:
- **Stock Symbol** (Title)
- **Company Name** (Rich Text)
- **Current Price** (Number)
- **Prev Close** (Number)
- **Price Change** (Number)
- **Change Percentage** (Number)
- **Volume** (Number)
- **Market Cap** (Number)
- **52-Week High/Low** (Rich Text)
- **Exchange** (Select)
- **Last Updated** (Date)

### Portfolio Database (Optional)
For portfolio tracking:
- **Stock Symbol** (Title)
- **Shares Owned** (Number)
- **Purchase Price** (Number, Currency)
- **Date** (Date)
- **Total Value** (Number, Currency)

## 🎯 Usage Guide

### Adding Stocks
1. Enter stock symbol (e.g., AAPL, GOOGL)
2. Click "Add Stock"
3. Stock data automatically populates in Notion

### Updating Prices
1. Click "Update Stocks" for all stocks
2. Or enter specific symbols to update selected stocks
3. All data syncs to your Notion databases

### Portfolio Tracking
1. Add "Shares Owned" and "Purchase Price" columns to your main database
2. Enter your holdings for each stock
3. Click "Load Portfolio Summary" to see real-time metrics

### Daily Snapshots
1. Click "Create Portfolio Snapshot"
2. Daily portfolio values are saved for historical analysis
3. Export data from Notion for charting and analysis

## 🔄 API Endpoints

- `GET /api/stocks` - Get list of tracked stocks
- `POST /api/stocks/update` - Update stock prices
- `POST /api/stocks/add` - Add new stock
- `GET /api/portfolio/summary` - Get portfolio metrics
- `POST /api/portfolio/snapshot` - Create portfolio snapshot
- `GET /health` - Health check endpoint

## 🎨 Design Features

- **Modern UI**: Clean, professional interface with gradient backgrounds
- **Responsive Design**: Works on all screen sizes
- **Interactive Elements**: Hover effects and smooth animations
- **Real-time Updates**: Live data loading with progress indicators
- **Mobile Optimized**: Touch-friendly interface for mobile devices

## 🔒 Security

- Environment variables for sensitive data
- CORS enabled for secure API access
- Input validation and error handling
- Secure Notion API integration

## 📈 Performance

- Efficient API calls with rate limiting
- Background processing for long operations
- Optimized database queries
- Fast loading times with minimal dependencies

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section below
2. Review Notion database setup
3. Verify environment variables
4. Check Railway deployment logs

## 🔧 Troubleshooting

### Common Issues

**Stock data not updating:**
- Verify Notion integration token
- Check database permissions
- Ensure database IDs are correct

**Portfolio not showing:**
- Add "Shares Owned" and "Purchase Price" columns
- Enter portfolio data in main database
- Click "Load Portfolio Summary"

**Deployment issues:**
- Check Railway environment variables
- Verify requirements.txt is up to date
- Review deployment logs in Railway dashboard

## 🎉 Acknowledgments

- Yahoo Finance API for stock data
- Notion API for database integration
- Railway for hosting platform
- Flask framework for web application

---

Built with ❤️ for professional stock portfolio management

