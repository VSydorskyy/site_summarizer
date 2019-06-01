from flask import request, jsonify, Response, Flask
from flask_cors import CORS

from summarizer_service.nlp.summarizer import summarize_pipeline

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello_world():
    return 'Summary service'


@app.route('/apply', methods=['POST'])
def apply():
    """ Generates and returns summary of the web page """
    params = request.json

    sent_num: int = int(params['sent_num'])
    html: str = params['html']
    url: str = params['url']

    site_summary = summarize_pipeline(html, sent_num)

    return jsonify({'generated_description': site_summary, 'additional_description': '', 'status': 'ok'})


@app.route('/send', methods=['POST'])
def send():
    return Response(status=400)
