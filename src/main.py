import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from datetime import datetime
import logging

# Import the stock integration class
from stock_integration import ImprovedStockNotionIntegrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Environment variables - MUST be loaded from Railway
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
STOCK_DATABASE_ID = os.environ.get('STOCK_DATABASE_ID')
PORTFOLIO_DATABASE_ID = os.environ.get('PORTFOLIO_DATABASE_ID')

# Debug: Print environment variable status (without exposing full values)
print("🔧 Environment Variables Status:")
print(f"   NOTION_TOKEN: {'✅ Set' if NOTION_TOKEN else '❌ Missing'}")
print(f"   STOCK_DATABASE_ID: {'✅ Set' if STOCK_DATABASE_ID else '❌ Missing'}")
print(f"   PORTFOLIO_DATABASE_ID: {'✅ Set' if PORTFOLIO_DATABASE_ID else '❌ Missing'}")

if NOTION_TOKEN:
    print(f"   Token starts with: {NOTION_TOKEN[:10]}...")
if STOCK_DATABASE_ID:
    print(f"   Stock DB ID starts with: {STOCK_DATABASE_ID[:10]}...")

# Validate required environment variables
if not NOTION_TOKEN:
    logger.error("❌ NOTION_TOKEN environment variable is missing!")
    raise ValueError("NOTION_TOKEN environment variable is required")

if not STOCK_DATABASE_ID:
    logger.error("❌ STOCK_DATABASE_ID environment variable is missing!")
    raise ValueError("STOCK_DATABASE_ID environment variable is required")

# Initialize the stock integrator with environment variables
try:
    integrator = ImprovedStockNotionIntegrator(
        notion_token=NOTION_TOKEN,
        stock_database_id=STOCK_DATABASE_ID,
        portfolio_database_id=PORTFOLIO_DATABASE_ID
    )
    print("✅ Stock integrator initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize stock integrator: {str(e)}")
    raise

@app.route('/')
def index():
    """Serve the main dashboard page"""
    try:
        static_folder_path = os.path.join(os.path.dirname(__file__), 'static')
        index_path = os.path.join(static_folder_path, 'index.html')
        
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404
    except Exception as e:
        logger.error(f"Error serving index page: {str(e)}")
        return f"Error loading page: {str(e)}", 500

@app.route('/api/stocks/remove', methods=['POST'])
def remove_stock():
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Symbol is required'})
        
        # Remove from Notion database
        integrator.remove_stock_from_database(symbol)
        
        return jsonify({'success': True, 'message': f'Successfully removed {symbol}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment_variables': {
            'notion_token': 'set' if NOTION_TOKEN else 'missing',
            'stock_database_id': 'set' if STOCK_DATABASE_ID else 'missing',
            'portfolio_database_id': 'set' if PORTFOLIO_DATABASE_ID else 'missing'
        }
    })

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get list of tracked stocks"""
    try:
        # Try to get stocks from database, fall back to default if needed
        stocks = integrator.get_stocks_from_database()
        
        return jsonify({
            'success': True,
            'stocks': stocks,
            'count': len(stocks)
        })
    except Exception as e:
        logger.error(f"Error getting stocks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'stocks': integrator.default_stocks,
            'count': len(integrator.default_stocks)
        })

@app.route('/api/stocks/update', methods=['POST'])
def update_stocks():
    """Update stock prices"""
    try:
        data = request.get_json() or {}
        symbols = data.get('symbols', None)
        
        # Update stocks
        updated_count, failed_count = integrator.update_stocks(symbols)
        
        return jsonify({
            'success': True,
            'updated': updated_count,
            'failed': failed_count,
            'message': f'Updated {updated_count} stocks, {failed_count} failed'
        })
    except Exception as e:
        logger.error(f"Error updating stocks: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/stocks/add', methods=['POST'])
def add_stock():
    """Add a new stock to tracking"""
    try:
        data = request.get_json()
        if not data or 'symbol' not in data:
            return jsonify({
                'success': False,
                'error': 'Stock symbol is required'
            }), 400
        
        symbol = data['symbol'].upper().strip()
        
        # Add the stock
        success = integrator.add_stock(symbol)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully added {symbol} to tracking'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to add {symbol}'
            })
    except Exception as e:
        logger.error(f"Error adding stock: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """Get portfolio summary"""
    try:
        summary = integrator.get_portfolio_summary()
        
        return jsonify({
            'success': True,
            'portfolio': summary
        })
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'portfolio': {
                'total_value': 0,
                'total_investment': 0,
                'gain_loss': 0,
                'return_percentage': 0,
                'positions': 0
            }
        })

@app.route('/api/portfolio/snapshot', methods=['POST'])
def create_portfolio_snapshot():
    """Create a portfolio snapshot"""
    try:
        success = integrator.create_portfolio_snapshot()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Portfolio snapshot created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create portfolio snapshot'
            })
    except Exception as e:
        logger.error(f"Error creating portfolio snapshot: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Stock-Notion Portfolio Dashboard...")
    print("📊 Features enabled:")
    print("   ✅ Dynamic stock detection")
    print("   ✅ Real-time price updates")
    print("   ✅ Portfolio tracking")
    print("   ✅ Historical snapshots")
    print("   ✅ Automatic integration")
    print()
    
    # Use Railway's PORT environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

