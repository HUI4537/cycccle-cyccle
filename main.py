from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_mysqldb import MySQL
import os
import sqlite3
import base64
import uuid
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import hashlib
import os
import json
import re
#경로 가져오기
from place_recommender import PlaceRecommender
from route_finder import get_route, get_waypoints
import pandas as pd

app = Flask(__name__)
CORS(app)  # CORS 설정 추가

app.secret_key = app.secret_key or 'default_secret_key'

import sqlite3  # SQLite 모듈 추가

# SQLite 데이터베이스 파일 경로
LOGIN_DATABASE_FILE = os.path.join(os.path.dirname(__file__), "pythonlogin.db")
LOGIN_DATA_FILE = os.path.join(app.static_folder, "Main", "data.json")

def get_logindb_connection():
    """SQLite 데이터베이스 연결 함수."""
    conn = sqlite3.connect(LOGIN_DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # 딕셔너리처럼 결과를 반환하기 위해 추가
    return conn




# 현재 Python 파일의 디렉터리 기준으로 경로 설정
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BOARD_DATABASE = os.path.join(BASE_DIR, 'board.db')
BOARD_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    

def get_budb_connection():
    conn = sqlite3.connect(BOARD_DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def load_data():
    if not os.path.exists(LOGIN_DATA_FILE):
        return {"error": "Data file not found"}
    try:
        with open(LOGIN_DATA_FILE, encoding="utf-8") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in data file"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

@app.route("/")
def main():
    return render_template("Main.html")

@app.route("/Main")
def gomain():
    return render_template("Main.html")

@app.route("/api/data")
def api_data():
    data = load_data()
    if "error" in data:
        return jsonify(data), 500  # 오류가 발생하면 HTTP 500 반환
    return jsonify(data), 200  # 성공 시 HTTP 200 반환


@app.route('/picture/<path:filename>')
def picture(filename):
    return send_from_directory("picture", filename)

# 로그인 페이지
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        hash = hashlib.sha1((password + app.secret_key).encode()).hexdigest()

        conn = get_logindb_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = ? AND password = ?', (username, hash))
        account = cursor.fetchone()
        conn.close()

        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)


# 로그아웃
@app.route('/pythonlogin/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# 회원가입 페이지
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        conn = get_logindb_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = ?', (username,))
        account = cursor.fetchone()

        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        else:
            hash = hashlib.sha1((password + app.secret_key).encode()).hexdigest()
            cursor.execute('INSERT INTO accounts (username, password, email) VALUES (?, ?, ?)', (username, hash, email))
            conn.commit()
            msg = 'You have successfully registered!'
        conn.close()
    return render_template('register.html', msg=msg)

# 홈 페이지
@app.route('/pythonlogin/home')
def home():
    if 'loggedin' in session:
        return render_template('Main.html', username=session['username'], loggedin=True)
    return redirect(url_for('login'))

# 프로필 페이지
@app.route('/pythonlogin/profile')
def profile():
    if 'loggedin' in session:
        conn = get_logindb_connection()
        cursor = conn.cursor()
        
        # 사용자 정보 가져오기
        cursor.execute('SELECT * FROM accounts WHERE id = ?', (session['id'],))
        account = cursor.fetchone()
        
        # 사용자의 트랙 정보 가져오기
        cursor.execute('''
            SELECT * FROM tracks 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        ''', (session['id'],))
        tracks = cursor.fetchall()
        
        conn.close()
        return render_template('profile.html', account=account, tracks=tracks, loggedin=True)
    return redirect(url_for('login'))


@app.context_processor
def inject_loggedin_status():
    return {'loggedin': 'loggedin' in session}

###
#여기 아래부터 게시판 관련 라우터
#---------------------------------------------------------------------------------
###

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/post/<int:post_id>')
def post(post_id):
    return render_template('post.html')

# API 엔드포인트 - 게시글 목록 조회
@app.route('/api/posts', methods=['GET'])
def get_posts():
    conn = get_budb_connection()
    
    # posts와 images 테이블 조인 (각 post_id에 대해 첫 번째 이미지만 가져옴)
    query = """
        SELECT p.*, 
               (SELECT image_url 
                FROM images 
                WHERE images.post_id = p.id 
                ORDER BY id ASC 
                LIMIT 1) AS thumbnail
        FROM posts p
    """
    posts = conn.execute(query).fetchall()
    conn.close()
    
    # 데이터를 JSON 형태로 변환
    return jsonify([dict(post) for post in posts])


# API 엔드포인트 - 특정 게시글 조회
@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    conn = get_budb_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?', (post_id,)).fetchone()
    images = conn.execute('SELECT image_url FROM images WHERE post_id = ?', (post_id,)).fetchall()
    comments = conn.execute('SELECT * FROM comments WHERE post_id = ?', (post_id,)).fetchall()
    conn.close()

    if post is None:
        return jsonify({'error': 'Post not found'}), 404

    return jsonify({
        'post': dict(post),
        'images': [image['image_url'] for image in images],
        'comments': [dict(comment) for comment in comments]
    })

# API 엔드포인트 - 게시글 좋아요 증가
@app.route('/api/posts/<int:post_id>/like', methods=['POST'])
def toggle_post_like(post_id):
    conn = get_budb_connection()
    cursor = conn.cursor()

    # 요청 데이터에서 좋아요 상태 받기
    data = request.get_json()
    is_liked = data.get('is_liked', True)

    # 좋아요 상태에 따라 증가/감소 처리
    if is_liked:
        cursor.execute('UPDATE posts SET likes = likes + 1 WHERE id = ?', (post_id,))
    else:
        cursor.execute('UPDATE posts SET likes = likes - 1 WHERE id = ?', (post_id,))

    conn.commit()

    # 변경된 좋아요 수 반환
    updated_likes = cursor.execute('SELECT likes FROM posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()

    if updated_likes:
        return jsonify({'success': True, 'likes': updated_likes[0]})
    else:
        return jsonify({'success': False}), 404

#댓글달기
@app.route('/api/comments', methods=['POST'])
def add_comment():
    data = request.get_json()
    post_id = data.get('post_id')
    user_id = data.get('user_id')
    content = data.get('content')
    
    if not post_id or not user_id or not content:
        return jsonify({'error': 'Invalid data'}), 400
    
    conn = get_budb_connection()
    cursor = conn.cursor()
    
    # 댓글 추가
    cursor.execute(
        'INSERT INTO comments (post_id, user_id, content) VALUES (?, ?, ?)',
        (post_id, user_id, content)
    )
    
    # 정확한 댓글 수 계산 및 업데이트
    cursor.execute(
        'SELECT COUNT(*) FROM comments WHERE post_id = ?',
        (post_id,)
    )
    comment_count = cursor.fetchone()[0]
    
    cursor.execute(
        'UPDATE posts SET comment_count = ? WHERE id = ?',
        (comment_count, post_id)
    )
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Comment added successfully'}), 201
@app.route('/api/comments/<int:comment_id>/like', methods=['POST'])
def toggle_comment_like(comment_id):
    conn = get_budb_connection()
    cursor = conn.cursor()

    # 요청 데이터에서 좋아요 상태 받기
    data = request.get_json()
    is_liked = data.get('is_liked', True)

    # 좋아요 상태에 따라 증가/감소 처리
    if is_liked:
        cursor.execute('UPDATE comments SET likes = likes + 1 WHERE id = ?', (comment_id,))
    else:
        cursor.execute('UPDATE comments SET likes = likes - 1 WHERE id = ?', (comment_id,))

    conn.commit()

    # 변경된 좋아요 수 반환
    updated_likes = cursor.execute('SELECT likes FROM comments WHERE id = ?', (comment_id,)).fetchone()
    conn.close()

    if updated_likes:
        return jsonify({'success': True, 'likes': updated_likes[0]})
    else:
        return jsonify({'success': False}), 404

#게시글 업로드
@app.route('/api/posts', methods=['POST'])
def create_post():
    try:
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        print("Received data:", data)  # 디버깅을 위한 데이터 출력
        
        required_fields = ['title', 'content', 'user_id']
        if not all(field in data for field in required_fields):
            return jsonify({'error': f'Missing required fields. Required: {required_fields}'}), 400
        
        conn = get_budb_connection()
        try:
            # 게시글 저장
            cursor = conn.execute(
                '''INSERT INTO posts (user_id, title, content, route_code)
                   VALUES (?, ?, ?, ?)''',
                (data['user_id'], 
                 data['title'], 
                 data['content'],
                 data.get('route_code', ''))
            )
            
            post_id = cursor.lastrowid
            
            # 이미지 처리
            if 'images' in data and data['images']:
                for image_data in data['images']:
                    if image_data:
                        try:
                            # Base64 이미지 데이터 저장
                            image_url = save_base64_image(image_data, post_id)
                            if image_url:
                                conn.execute(
                                    'INSERT INTO images (post_id, image_url) VALUES (?, ?)',
                                    (post_id, image_url)
                                )
                        except Exception as e:
                            print(f"Error saving image: {e}")
                            continue
            
            conn.commit()
            return jsonify({'success': True, 'post_id': post_id})
            
        except Exception as e:
            conn.rollback()
            print(f"Database error: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Server error: {e}")
        return jsonify({'error': str(e)}), 500

def save_base64_image(base64_string, post_id):
    try:
        # base64 헤더 제거
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
            
        # base64 디코드
        image_data = base64.b64decode(base64_string)
        
        # 파일명 생성
        filename = f"post_{post_id}_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 이미지 저장
        with open(filepath, 'wb') as f:
            f.write(image_data)
            
        return f'/static/uploads/{filename}'
    except Exception as e:
        print(f"Error in save_base64_image: {e}")
        return None

# 데이터베이스 초기화 함수
def setup_database():
    conn = get_budb_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                route_code TEXT,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER NOT NULL,
                image_url TEXT NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts (id)
            )
        ''')
        
        conn.commit()
    except Exception as e:
        print(f"Database setup error: {e}")
        conn.rollback()
    finally:
        conn.close()

#추천 페이지 및 경로 ---------------------------------------------------------------------------------------


from place_recommender import PlaceRecommender
import pandas as pd



# 추천 페이지 라우트
@app.route('/Recommend')
def Recommend():
    # 변수 초기화
    restaurant_data = pd.DataFrame()  # 빈 DataFrame으로 초기화
    recommended_places = []  # 추천 장소 리스트 초기화

    try:
        # restaurant.csv 파일 로드
        csv_path = '11-1SWhack/khg/restaurant.csv'
        restaurant_data = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        print(f"Current working directory: {os.getcwd()}")
        return render_template('Recommend.html', recommended_places=[])  # 에러 시 빈 리스트 반환

    age_range = request.args.get('age_range')
    gender = request.args.get('gender')
    nationality = request.args.get('nationality')
    travel_pref = request.args.get('travel_pref')
    food_pref = request.args.get('food_pref')

    # 샘플 데이터
    user_profiles = {
        "user1": {"age_range": "10대", "gender": "여성", "nationality": "한국", "travel_pref": "상큼 발랄한 여름", "food_pref": "밥 요리"},
        "user2": {"age_range": "20대", "gender": "남성", "nationality": "한국", "travel_pref": "도시 탐방", "food_pref": "면 요리"},
        "user3": {"age_range": "30대", "gender": "여성", "nationality": "미국", "travel_pref": "문화적 체험", "food_pref": "채식"},
        "user4": {"age_range": "40대", "gender": "남성", "nationality": "일본", "travel_pref": "자연 속 휴식", "food_pref": "해산물"},
        "user5": {"age_range": "10대", "gender": "여성", "nationality": "일본", "travel_pref": "활동적인 여행", "food_pref": "분식"},
    }

    user_place_matrix = {
        "user1": {2: 1, 6: 1, 122: 1},
        "user2": {5: 1, 8: 1, 10: 1},
        "user3": {2: 1, 4: 1, 15: 1},
        "user4": {3: 1, 6: 1, 7: 1},
        "user5": {1: 1, 9: 1, 12: 1},
    }

    if age_range is None or gender is None or nationality is None or travel_pref is None or food_pref is None:
        recommended_places = []
        print("Parameters missing")
    else:
        try:
            # 새로운 사용자 프로필
            new_user_profile = {"age_range": age_range, "gender": gender, "nationality": nationality, 
                              "travel_pref": travel_pref, "food_pref": food_pref}
            
            # 추천 시스템 초기화 및 추천 실행
            recommender = PlaceRecommender(user_profiles, user_place_matrix)
            recommended_place_ids = recommender.place_recommend(new_user_profile)

            # 추천된 장소 ID를 기반으로 restaurant_data에서 해당 장소 정보 가져오기
            recommended_places = restaurant_data[restaurant_data.index.isin(recommended_place_ids)].to_dict('records')
        except Exception as e:
            print(f"Error in recommendation process: {e}")
            recommended_places = []

    return render_template('Recommend.html', recommended_places=recommended_places)

@app.route('/Survey')
def survey():
    return render_template('Survey.html')

@app.route('/Order')
def Order():
    # URL에서 선택된 장소들을 가져옵니다
    selected_places = request.args.getlist('places')
    
    if not selected_places:
        return redirect(url_for('Recommend'))
        
    return render_template('Order.html', place_list=selected_places)

@app.route('/save_order', methods=['POST'])
def save_order():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    data = request.get_json()
    ordered_places = data.get('orderedPlaces', [])
    
    if not ordered_places:
        return jsonify({'error': 'No places provided'}), 400
        
    # 장소들을 쉼표로 구분된 문자열로 변환
    track_places = ','.join(ordered_places)
    
    try:
        conn = get_logindb_connection()
        cursor = conn.cursor()
        
        # 트랙 정보를 데이터베이스에 저장
        cursor.execute('''
            INSERT INTO tracks (user_id, track_places)
            VALUES (?, ?)
        ''', (session['id'], track_places))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '트랙이 저장되었습니다.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/Journey')
def Journey():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    # 데이터베이스에서 사용자의 가장 최근 트랙 정보 가져오기
    conn = get_logindb_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT track_places 
        FROM tracks 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 1
    ''', (session['id'],))
    track = cursor.fetchone()
    conn.close()

    if not track:
        return "저장된 트랙이 없습니다.", 400

    # 쉼표로 구분된 장소 문자열을 리스트로 변환
    place_names = track['track_places'].split(',')
    
    # 가게 이름으로 경유지 좌표 가져오기
    waypoints = get_waypoints(place_names)  # get_waypoints 함수가 올바른 형식으로 반환한다고 가정
    if not waypoints or len(waypoints) < 2:
        return "Insufficient waypoints for route calculation", 400
    
    # Tmap API를 통해 경로 데이터 가져오기
    route_data = get_route(waypoints)  # get_route 함수가 API 요청 및 응답을 처리한다고 가정
    if not route_data or 'features' not in route_data:
        return "Failed to retrieve route data", 500

    # 경로 데이터에서 라인 좌표 추출
    route_points = []
    try:
        for feature in route_data['features']:
            # 라인스트링(LineString) 데이터인지 확인
            if feature['geometry']['type'] == 'LineString':
                # 라인 좌표를 경로 포인트로 변환
                for coordinate in feature['geometry']['coordinates']:
                    # 좌표가 [longitude, latitude] 형식이라면 변환
                    route_points.append({
                        "lat": float(coordinate[1]),  # 위도
                        "lng": float(coordinate[0])  # 경도
                    })
    except Exception as e:
        return f"Error processing route data: {str(e)}", 500
    # 경로 포인트를 지도에 전달
    return render_template('Journey.html', route_points=f"{route_points}".replace("'",'"'))


if __name__ == "__main__":
    app.run(debug=True)
