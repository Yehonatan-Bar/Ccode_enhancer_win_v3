from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('game_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ping-pong-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True, async_mode='threading')

# Game state
game_state = {
    'players': {},
    'scores': {'player1': 0, 'player2': 0},
    'ball': {'x': 400, 'y': 300, 'vx': 5, 'vy': 3},
    'paddles': {
        'player1': {'y': 250, 'score': 0},
        'player2': {'y': 250, 'score': 0}
    },
    'game_active': False
}

@app.route('/')
def index():
    logger.info("Game page requested")
    return render_template('index.html')

@app.route('/api/status')
def status():
    logger.info("Status endpoint called")
    return jsonify({
        'status': 'running',
        'players_connected': len(game_state['players']),
        'game_active': game_state['game_active'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/scores')
def get_scores():
    logger.info(f"Scores requested: {game_state['scores']}")
    return jsonify(game_state['scores'])

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connected', {'id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    if request.sid in game_state['players']:
        del game_state['players'][request.sid]
        emit('player_left', {'players': len(game_state['players'])}, broadcast=True)

@socketio.on('join_game')
def handle_join_game(data):
    player_name = data.get('name', f'Player_{request.sid[:6]}')
    logger.info(f"Player joining: {player_name}")
    
    player_num = len(game_state['players']) + 1
    if player_num <= 2:
        game_state['players'][request.sid] = {
            'name': player_name,
            'player_num': player_num,
            'ready': False
        }
        emit('player_joined', {
            'player_num': player_num,
            'players': len(game_state['players'])
        }, broadcast=True)
        logger.info(f"Player {player_name} joined as Player {player_num}")
    else:
        emit('game_full', {})
        logger.warning(f"Player {player_name} tried to join but game is full")

@socketio.on('player_ready')
def handle_player_ready():
    if request.sid in game_state['players']:
        game_state['players'][request.sid]['ready'] = True
        logger.info(f"Player {request.sid} is ready")
        
        # Check if all players are ready
        if len(game_state['players']) == 2 and all(p['ready'] for p in game_state['players'].values()):
            game_state['game_active'] = True
            emit('game_start', {}, broadcast=True)
            logger.info("Game started!")

@socketio.on('paddle_move')
def handle_paddle_move(data):
    if request.sid in game_state['players']:
        player_num = game_state['players'][request.sid]['player_num']
        player_key = f'player{player_num}'
        game_state['paddles'][player_key]['y'] = data['y']
        
        emit('paddle_update', {
            'player': player_key,
            'y': data['y']
        }, broadcast=True, include_self=False)
        
        logger.debug(f"Paddle moved - {player_key}: y={data['y']}")

@socketio.on('ball_update')
def handle_ball_update(data):
    game_state['ball'] = data
    emit('ball_position', data, broadcast=True, include_self=False)
    logger.debug(f"Ball position: x={data['x']}, y={data['y']}")

@socketio.on('score_update')
def handle_score_update(data):
    player = data['player']
    game_state['scores'][player] += 1
    logger.info(f"Score update - {player}: {game_state['scores'][player]}")
    
    emit('score_changed', game_state['scores'], broadcast=True)
    
    # Check for game win
    if game_state['scores'][player] >= 5:
        game_state['game_active'] = False
        emit('game_over', {'winner': player}, broadcast=True)
        logger.info(f"Game over! Winner: {player}")

@socketio.on('reset_game')
def handle_reset_game():
    logger.info("Game reset requested")
    game_state['scores'] = {'player1': 0, 'player2': 0}
    game_state['ball'] = {'x': 400, 'y': 300, 'vx': 5, 'vy': 3}
    game_state['paddles'] = {
        'player1': {'y': 250, 'score': 0},
        'player2': {'y': 250, 'score': 0}
    }
    for player in game_state['players'].values():
        player['ready'] = False
    game_state['game_active'] = False
    
    emit('game_reset', {}, broadcast=True)
    logger.info("Game has been reset")

if __name__ == '__main__':
    logger.info("Starting Ping Pong Game Server...")
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')