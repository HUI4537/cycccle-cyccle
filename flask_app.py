from flask import Flask, render_template, request
from place_recommender import PlaceRecommender
import pandas as pd

# Flask 애플리케이션 인스턴스 생성
app = Flask(__name__)

# 홈 페이지 라우트
@app.route('/')
def Home():
    return render_template('Home.html')

# 추천 페이지 라우트
@app.route('/Recommend')
def Recommend():
    # restaurant.csv 파일 로드
    restaurant_data = pd.read_csv('C:/Users/perfe/OneDrive/Desktop/2학년 활동/동아리/FINDER/선정된 외부 활동/SW 동행 프로젝트(최성민, ect...) - selected/해커톤(최성민, 서승기, 김한결, 김건민, 김선민)/ccycleccycle/restaurant.csv')

    
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
        print("fuck")
    else:
        # 새로운 사용자 프로필
        new_user_profile = {"age_range": age_range, "gender": gender, "nationality": nationality, "travel_pref": travel_pref, "food_pref": food_pref}
        
        # 추천 시스템 초기화 및 추천 실행
        recommender = PlaceRecommender(user_profiles, user_place_matrix)
        recommended_place_ids = recommender.place_recommend(new_user_profile)

        # 추천된 장소 ID를 기반으로 restaurant_data에서 해당 장소 정보 가져오기
        recommended_places = restaurant_data[restaurant_data.index.isin(recommended_place_ids)].to_dict('records')

    return render_template('Recommend.html', recommended_places=recommended_places)

# Flask 애플리케이션 실행
if __name__ == '__main__':
    app.run(debug=True)
