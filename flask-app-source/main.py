from flask import Flask, jsonify, request
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/hello', methods=['GET'])
def helloworld():
	if request.method == 'GET':
		api_key = os.environ.get('SUPER_SECRET_KEY')
		if api_key:
			logger.info("Secret successfully loaded")
		data = {"data": "Hello World"}
		return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)