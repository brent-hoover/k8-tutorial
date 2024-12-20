from flask import Flask, jsonify, request
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def helloworld():
	if request.method == 'GET':
		secret1 = os.environ.get('SUPER_SECRET_KEY')
		secret2 = os.environ.get('ANOTHER_SECRET_KEY')
		if secret1 and secret2:
			logger.info(f"Secrets loaded - SUPER_SECRET_KEY: {secret1}, ANOTHER_SECRET_KEY: {secret2}")
		else:
			logger.warning("One or more secrets not found")
		data = {"data": "Hello World"}
		return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)