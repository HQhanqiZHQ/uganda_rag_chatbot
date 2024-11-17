from flask import Flask, render_template, request, jsonify
from src.evaluation.evaluator import MediTronEvaluator

# Create Flask app
evaluation_app = Flask(__name__)
evaluator = MediTronEvaluator()

@evaluation_app.route('/')
def home():
    return render_template('evaluation.html')

@evaluation_app.route('/evaluate', methods=['POST'])
def evaluate():
    """
    Evaluate the query, response, and reference using MediTronEvaluator.
    """
    data = request.json
    query = data.get("query")
    response = data.get("response")
    reference = data.get("reference")

    if not query or not response or not reference:
        return jsonify({"error": "All fields (query, response, reference) are required."}), 400

    # Evaluate the inputs
    results = evaluator.evaluate_response(query, response, reference)
    return jsonify(results)

if __name__ == '__main__':
    evaluation_app.run(debug=True, host='0.0.0.0', port=8000)
