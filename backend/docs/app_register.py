from api.routes.defi_routes import defi_bp  # ADD THIS
from api.routes.ner_routes import ner_bp  # your existing NER routes
from flask import Flask

app = Flask(__name__)

# Register blueprints
app.register_blueprint(ner_bp)
app.register_blueprint(defi_bp)  # ADD THIS

if __name__ == "__main__":
    app.run(debug=True, port=5000)
