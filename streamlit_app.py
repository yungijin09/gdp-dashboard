
#### 3. [streamlit_app.py 전체 코드]

# streamlit_app.py

import streamlit as st
import random
import time

# --- 게임 설정 ---
SCREEN_WIDTH = 40
GROUND_LEVEL = 1
DINO_CHAR = "🦖"
OBSTACLE_CHAR = "🌵"
EMPTY_CHAR = " "

# --- 게임 상태 초기화 함수 ---
def initialize_game():
    """게임에 필요한 모든 상태 변수를 st.session_state에 초기화합니다."""
    st.session_state.dino_y = GROUND_LEVEL  # 공룡의 y좌표
    st.session_state.dino_velocity = 0  # 공룡의 수직 속도 (점프용)
    st.session_state.gravity = -2.5      # 중력 값
    st.session_state.jump_strength = 9  # 점프 강도
    st.session_state.is_jumping = False   # 점프 상태 여부

    st.session_state.obstacles = []       # 장애물 리스트
    st.session_state.score = 0            # 점수
    st.session_state.game_over = False    # 게임 오버 상태
    st.session_state.frame_count = 0      # 장애물 생성 타이밍 조절용

# --- 메인 게임 로직 ---

# 앱 제목 설정
st.title("🦕 Streamlit 공룡 게임 🌵")

# st.session_state가 초기화되지 않았다면 게임 시작 상태로 설정
if 'game_started' not in st.session_state:
    st.session_state.game_started = False

# 시작 화면
if not st.session_state.game_started:
    if st.button("🚀 게임 시작하기"):
        st.session_state.game_started = True
        initialize_game()
        st.rerun() # 버튼 클릭 시 즉시 게임 화면으로 전환

# 게임이 시작된 경우
else:
    # 게임 오버 화면
    if st.session_state.game_over:
        st.error(f"GAME OVER! 최종 점수: {st.session_state.score}", icon="💀")
        if st.button("다시 시작하기"):
            initialize_game() # 게임 상태 초기화
            st.rerun() # 즉시 재시작
    
    # 게임 진행 화면
    else:
        # --- 입력 처리 ---
        # '점프' 버튼을 누르면 공룡의 점프 상태를 활성화
        if st.button("점프!", use_container_width=True):
            if not st.session_state.is_jumping:
                st.session_state.is_jumping = True
                st.session_state.dino_velocity = st.session_state.jump_strength

        # --- 게임 상태 업데이트 ---
        
        # 1. 점수 및 프레임 증가
        st.session_state.score += 1
        st.session_state.frame_count += 1

        # 2. 공룡 위치 업데이트 (점프 및 중력)
        if st.session_state.is_jumping:
            st.session_state.dino_y += st.session_state.dino_velocity
            st.session_state.dino_velocity += st.session_state.gravity
            
            # 땅에 닿으면 점프 상태 초기화
            if st.session_state.dino_y <= GROUND_LEVEL:
                st.session_state.dino_y = GROUND_LEVEL
                st.session_state.is_jumping = False
                st.session_state.dino_velocity = 0
        
        # 3. 장애물 이동 및 생성
        # 장애물 위치를 왼쪽으로 한 칸씩 이동
        for obstacle in st.session_state.obstacles:
            obstacle['x'] -= 1
        
        # 화면 밖으로 나간 장애물 제거
        st.session_state.obstacles = [ob for ob in st.session_state.obstacles if ob['x'] > 0]
        
        # 일정 프레임마다 무작위로 새로운 장애물 생성
        if st.session_state.frame_count % random.randint(25, 40) == 0:
            st.session_state.obstacles.append({'x': SCREEN_WIDTH - 1})

        # 4. 충돌 감지
        dino_pos = 2  # 공룡은 화면 왼쪽에서 2번째 칸에 고정
        for obstacle in st.session_state.obstacles:
            # 공룡과 장애물의 x, y 좌표가 모두 겹치면 충돌
            if obstacle['x'] == dino_pos and st.session_state.dino_y <= GROUND_LEVEL:
                st.session_state.game_over = True

        # --- 화면 그리기 ---

        # 점수판 표시
        st.info(f"점수: {st.session_state.score}")

        # 게임 화면을 표시할 placeholder 생성
        game_canvas = st.empty()
        
        # 2D 그리드 생성 (하늘)
        grid = [[EMPTY_CHAR for _ in range(SCREEN_WIDTH)] for _ in range(12)]
        
        # 바닥 그리기
        for i in range(SCREEN_WIDTH):
            grid[GROUND_LEVEL-1][i] = "─"

        # 공룡 그리기 (정수 좌표에만)
        dino_render_y = min(len(grid) - 1, int(st.session_state.dino_y))
        grid[dino_render_y][dino_pos] = DINO_CHAR
        
        # 장애물 그리기
        for obstacle in st.session_state.obstacles:
            grid[GROUND_LEVEL][obstacle['x']] = OBSTACLE_CHAR
        
        # 그리드를 하나의 문자열로 변환하여 출력
        canvas_str = "\n".join(["".join(row) for row in reversed(grid)])
        game_canvas.code(canvas_str, language=None)
        
        # 게임 루프를 위한 지연 및 새로고침
        if not st.session_state.game_over:
            time.sleep(0.1) # 프레임 속도 조절
            st.rerun()