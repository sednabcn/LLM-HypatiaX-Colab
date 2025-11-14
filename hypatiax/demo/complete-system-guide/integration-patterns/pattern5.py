# Pattern 5: Web API Integration


# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from demo.engine import HypatiaXEngine

app = Flask(__name__)
CORS(app)

engine = HypatiaXEngine()

@app.route('/api/map', methods=['POST'])
def map_description():
    data = request.get_json()
    result = engine.process(
        query=data['description'],
        method=data.get('method', 'vocab')
    )
    
    return jsonify({
        'formula': result.formula,
        'entities': [
            {'text': e.text, 'label': e.label, 'start': e.start, 'end': e.end}
            for e in result.entities
        ],
        'confidence': result.confidence,
        'processing_time': result.processing_time
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
