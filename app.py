from flask import Flask, request, jsonify
from datetime import datetime
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

class SimpleLoanModel:
    def __init__(self):

        self.min_credit_score = 600
        self.min_income = 30000
        self.max_dti = 0.45
        
    def predict(self, data):

        score = 0
        
        if data['credit_score'] >= 750:
            score += 40
        elif data['credit_score'] >= 700:
            score += 30
        elif data['credit_score'] >= 650:
            score += 20
        elif data['credit_score'] >= 600:
            score += 10
        
        if data['annual_income'] >= 100000:
            score += 30
        elif data['annual_income'] >= 70000:
            score += 25
        elif data['annual_income'] >= 50000:
            score += 20
        elif data['annual_income'] >= 30000:
            score += 10
        
        if data['debt_to_income'] <= 0.2:
            score += 30
        elif data['debt_to_income'] <= 0.3:
            score += 25
        elif data['debt_to_income'] <= 0.4:
            score += 15
        elif data['debt_to_income'] <= 0.45:
            score += 5
        
        return score
    
    def get_recommendation(self, score, loan_amount, annual_income):

        if score >= 80:
            max_amount = annual_income * 2
            approved_amount = min(loan_amount, max_amount)
            interest_rate = 5.0
            
            return {
                "approval_status": "Approved",
                "approved_amount": approved_amount,
                "interest_rate": interest_rate,
                "message": f"Congratulations! You're approved for ${approved_amount:,.2f} at {interest_rate:.1f}% interest rate."
            }
            
        elif score >= 60:
            max_amount = annual_income * 1
            approved_amount = min(loan_amount, max_amount)
            interest_rate = 7.5
            
            return {
                "approval_status": "Conditionally Approved",
                "approved_amount": approved_amount,
                "interest_rate": interest_rate,
                "message": f"You're conditionally approved for ${approved_amount:,.2f} at {interest_rate:.1f}% interest rate."
            }
            
        elif score >= 40:
            max_amount = annual_income * 0.5
            approved_amount = min(loan_amount, max_amount)
            interest_rate = 9.0
            
            return {
                "approval_status": "Limited Approval",
                "approved_amount": approved_amount,
                "interest_rate": interest_rate,
                "message": f"You qualify for a limited loan of ${approved_amount:,.2f} at {interest_rate:.1f}% interest rate."
            }
            
        else:
            return {
                "approval_status": "Not Approved",
                "message": "Based on your information, we're unable to approve your loan at this time."
            }

loan_model = SimpleLoanModel()

@app.route('/api/loan-eligibility', methods=['POST'])
def evaluate_loan_eligibility():
    try:
        data = request.json
        
        required_fields = ['credit_score', 'annual_income', 'debt_to_income', 'loan_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400
        
        features = {
            'credit_score': float(data['credit_score']),
            'annual_income': float(data['annual_income']),
            'debt_to_income': float(data['debt_to_income']),
            'loan_amount': float(data['loan_amount'])
        }
        
        eligibility_score = loan_model.predict(features)
        
        recommendation = loan_model.get_recommendation(
            eligibility_score, 
            features['loan_amount'], 
            features['annual_income']
        )
        
        response = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'eligibility_score': eligibility_score,
            'recommendation': recommendation
        }
        
        logging.info(f"Processed loan request: ${features['loan_amount']} with score: {eligibility_score}")
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An error occurred processing your request'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'loan-eligibility-api',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)