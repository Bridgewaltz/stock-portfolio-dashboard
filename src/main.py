import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from datetime import datetime
import threading

# Import stock integration
from src.stock_integration import ImprovedStockNotionIntegrator

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
CORS(app)  # Enable CORS for all routes

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

# API Routes
@app.route('/api/stocks')
def get_stocks():
    """Get list of currently tracked stocks"""
    try:
        stocks = integrator.get_stocks_from_database()
        return jsonify({
            'success': True,
            'stocks': stocks,
            'count': len(stocks)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stocks/update', methods=['POST'])
def update_stocks():
    """Update stock prices"""
    try:
        data = request.get_json() or {}
        symbols = data.get('symbols', [])
        
        # If no specific symbols provided, update all stocks
        if not symbols:
            symbols = None
        
        # Run update in background thread to avoid timeout
        def run_update():
            integrator.update_stocks(symbols)
        
        thread = threading.Thread(target=run_update)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Stock update started',
            'symbols': symbols or 'all stocks'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stocks/add', methods=['POST'])
def add_stock():
    """Add a new stock to tracking"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({
                'success': False,
                'error': 'Stock symbol is required'
            }), 400
        
        # Run add in background thread
        def run_add():
            integrator.add_stock(symbol)
        
        thread = threading.Thread(target=run_add)
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Adding {symbol} with automatic integration',
            'symbol': symbol
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/portfolio/summary')
def get_portfolio_summary():
    """Get portfolio summary with current values"""
    try:
        summary = integrator.get_portfolio_summary()
        return jsonify({
            'success': True,
            'summary': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/portfolio/snapshot', methods=['POST'])
def create_portfolio_snapshot():
    """Create a daily portfolio snapshot"""
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
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'Enhanced Stock-Notion Portfolio Dashboard'
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

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

