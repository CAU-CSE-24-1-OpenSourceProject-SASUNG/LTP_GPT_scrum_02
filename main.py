from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

recent_items = [
    {'id': '1', 'label': '최근 항목 1'},
    {'id': '2', 'label': '최근 항목 2'},
    {'id': '3', 'label': '최근 항목 3'}
]

@app.route('/recentgames', methods=['GET'])
def get_recentgames():
    return jsonify(recent_items)


riddle_items = [
    {'riddleid': '1', 'label': '아이는 10층에 산다.'},
    {'riddleid': '2', 'label': '도청하는 사람 A'},
    {'riddleid': '3', 'label': '더운 방 속 한 사람'}
]

@app.route('/riddles', methods=['GET'])
def get_riddles():
    return jsonify(riddle_items)


newgame_items = [
    {'gameid': '100'},
]

@app.route('/newgame', methods=['GET'])
def get_newgame():
    return jsonify(newgame_items)


gameinfo_items = [
    {'problem': '어떤 아이가 아파트 10층에 살고 있다. 아이는 맑은 날 ~',
     'gptmsg' : 'gpt',
     'usermsg' : 'user',
     },
]

@app.route('/gameinfo', methods=['GET'])
def get_recent_items():
    return jsonify(gameinfo_items)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


