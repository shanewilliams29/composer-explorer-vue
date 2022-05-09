from app import app


# OLD CONFIG:

# from flask import Flask, jsonify
# from flask_cors import CORS


# # configuration
# # DEBUG = True

# # instantiate the app
# app = Flask(__name__, static_folder='dist', static_url_path='/')
# # app.config.from_object(__name__)

# # enable CORS
# CORS(app, resources={r'/*': {'origins': '*'}})


# @app.route('/')
# def index():
#     return app.send_static_file('index.html')


# @app.route('/ping', methods=['GET'])
# def ping_pong():
#     return jsonify('pong!')


# if __name__ == '__main__':
#     app.run(debug=True)
