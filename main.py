from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

recent_items = [
        {'id': '1', 'title': '아이는 10층에 산다 (1)'},
        {'id': '2', 'title': '더운 방 속 한 사람 (2)'},
        {'id': '3', 'title': '더운 방 속 한 사람 (1)'}
        ]

@app.route('/recentgames', methods=['GET'])
def get_recentgames():
    return jsonify(recent_items)


riddle_items = [
        {'id': '1', 'label': '아이는 10층에 산다.'},
        {'id': '2', 'label': '도청하는 사람 A'},
        {'id': '3', 'label': '더운 방 속 한 사람'}
        ]

@app.route('/riddles', methods=['GET'])
def get_riddles():
    return jsonify(riddle_items)


newgame = {'gameId': '3'}

@app.route('/newgame', methods=['POST'])
def get_newgame():
    data = request.get_json()
    user_id = data['userId']
    riddle_id = data['riddleId']
    return jsonify(newgame)


gameinfo = [
        {'gameTitle' : '아이는 10층에 산다. (1)', 'problem': '어떤 아이가 아파트 10층에 살고 있다. 아이는 맑은 날 ~'},
        {'queryId' : '1', 'query' : '안녕' , 'response' : '상관 없습니다.'},
        {'queryId' : '2', 'query' : '아이는 키가 작아?' , 'response' : '맞습니다.'},
        {'queryId' : '3', 'query' : '아이는 우산을 가지고 있어?' , 'response' : '맞습니다.'},
        {'queryId' : '4', 'query' : '아이는 운동하는 걸 좋아해?' , 'response' : '아닙니다.'},
        {'queryId' : '5', 'query' : '아이는 비오는 날 우산으로 10층 버튼을 누를 수 있는거야!' , 'response' : '정확한 정답을 맞추셨습니다!'},
        ]

@app.route('/gameinfo', methods=['POST'])
def get_gameinfo():
    return jsonify(gameinfo)

if __name__ == '__main__':
    app.run(debug=True, port=5000)


