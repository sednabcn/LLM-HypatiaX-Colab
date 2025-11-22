from flask import Blueprint, request, jsonify
from services.defi_calculator import DeFiCalculator

defi_bp = Blueprint('defi', __name__, url_prefix='/api/defi')
calculator = DeFiCalculator()

@defi_bp.route('/calculate-il', methods=['POST'])
def calculate_il():
    """Calculate impermanent loss"""
    data = request.get_json()
    
    try:
        result = calculator.calculate_il_percentage(
            current_price=float(data['current_price']),
            initial_price=float(data['initial_price'])
        )
        return jsonify({'il_percent': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@defi_bp.route('/calculate-quality-score', methods=['POST'])
def calculate_quality_score():
    """Calculate pool quality score"""
    data = request.get_json()
    
    try:
        result = calculator.calculate_quality_score(
            daily_volume_usd=float(data['daily_volume_usd']),
            fee_rate=float(data.get('fee_rate', 0.003)),
            position_value=float(data['position_value']),
            pool_tvl=float(data['pool_tvl']),
            il_dollar=float(data['il_dollar']),
            days_elapsed=int(data['days_elapsed'])
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@defi_bp.route('/analyze-position', methods=['POST'])
def analyze_position():
    """Complete LP position analysis"""
    data = request.get_json()
    
    try:
        result = calculator.calculate_position_analytics(
            initial_token_a=float(data['initial_token_a']),
            initial_token_b=float(data['initial_token_b']),
            initial_price=float(data['initial_price']),
            current_price=float(data['current_price']),
            days_elapsed=int(data['days_elapsed']),
            daily_volume=float(data['daily_volume']),
            pool_tvl=float(data['pool_tvl']),
            fee_rate=float(data.get('fee_rate', 0.003))
        )
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@defi_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'defi-calculator'}), 200
