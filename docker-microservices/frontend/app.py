from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

# API server connection details
API_HOST = 'backend-api'  # This will be the service name in docker-compose
API_PORT = 5001

@app.route('/')
def index():
    try:
        response = requests.get(f'http://{API_HOST}:{API_PORT}/sales')
        sales_data = response.json()
        return render_template('index.html', sales_data=sales_data)
    except requests.exceptions.RequestException as e:
        return render_template('error.html', error=str(e))

@app.route('/run-etl', methods=['POST'])
def run_etl():
    try:
        response = requests.post(f'http://{API_HOST}:{API_PORT}/run-etl')
        result = response.json()
        return render_template('etl_result.html', result=result)
    except requests.exceptions.RequestException as e:
        return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 