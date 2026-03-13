import cv2
import pygame
import numpy as np
import random
import time
from gesture import classify_gesture
from ai import AdaptiveAI
from game import Game
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp

# ── Window ──────────────────────────────────────────────────────────────────
WIDTH, HEIGHT = 1000, 600
CAM_W, CAM_H = 480, 360

# ── Colors ───────────────────────────────────────────────────────────────────
BLACK  = (10, 10, 10)
WHITE  = (240, 240, 240)
GREEN  = (0, 200, 100)
RED    = (220, 60, 60)
BLUE   = (60, 120, 220)
YELLOW = (240, 200, 0)
GRAY   = (60, 60, 60)
DARK   = (25, 25, 35)

# ── Gesture emoji map ────────────────────────────────────────────────────────
GESTURE_LABEL = {"rock": "✊ Rock", "paper": "✋ Paper", "scissors": "✌ Scissors", None: "..."}

def draw_text(surface, text, size, x, y, color=WHITE, center=False):
    font = pygame.font.SysFont("segoeui", size, bold=True)
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)

def frame_to_surface(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_resized = cv2.resize(frame_rgb, (CAM_W, CAM_H))
    return pygame.surfarray.make_surface(np.transpose(frame_resized, (1, 0, 2)))

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rock Paper Scissors AI")
    clock = pygame.time.Clock()

    # MediaPipe setup
    base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.7
    )
    detector = vision.HandLandmarker.create_from_options(options)

    cap = cv2.VideoCapture(0)

    # Game objects
    difficulty = "medium"
    best_of = 5
    ai = AdaptiveAI(difficulty)
    game = Game(best_of)

    # State machine
    # States: "menu" → "countdown" → "detecting" → "result" → "game_over"
    state = "menu"
    countdown_start = None
    countdown_val = 3
    detected_gesture = None
    ai_move = None
    round_result = None
    result_start = None
    current_frame_surface = None
    live_gesture = None

    RESULT_DISPLAY_TIME = 2.5  # seconds

    while True:
        ret, frame = cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = detector.detect(mp_image)

            live_gesture = None
            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
                live_gesture = classify_gesture(landmarks)
                h, w = frame.shape[:2]
                for lm in landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 100), -1)

            current_frame_surface = frame_to_surface(frame)

        # ── Events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if state == "menu":
                    if event.key == pygame.K_1:
                        difficulty = "easy";   ai = AdaptiveAI("easy")
                    elif event.key == pygame.K_2:
                        difficulty = "medium"; ai = AdaptiveAI("medium")
                    elif event.key == pygame.K_3:
                        difficulty = "hard";   ai = AdaptiveAI("hard")
                    elif event.key == pygame.K_b:
                        best_of = 3 if best_of == 5 else (7 if best_of == 3 else 5)
                        game = Game(best_of)
                    elif event.key == pygame.K_SPACE:
                        game.reset()
                        ai = AdaptiveAI(difficulty)
                        state = "countdown"
                        countdown_start = time.time()

                elif state == "game_over":
                    if event.key == pygame.K_SPACE:
                        state = "menu"
                        game.reset()
                        ai = AdaptiveAI(difficulty)

        # ── State Logic ──────────────────────────────────────────────────────
        if state == "countdown":
            elapsed = time.time() - countdown_start
            countdown_val = 3 - int(elapsed)
            if elapsed >= 3:
                state = "detecting"

        elif state == "detecting":
            if live_gesture:
                detected_gesture = live_gesture
                ai.record(detected_gesture)
                ai_move = ai.get_move()
                round_result = game.play_round(detected_gesture, ai_move)
                result_start = time.time()
                state = "result"

        elif state == "result":
            if time.time() - result_start > RESULT_DISPLAY_TIME:
                over = game.is_over()
                if over:
                    state = "game_over"
                else:
                    state = "countdown"
                    countdown_start = time.time()

        # ── Drawing ──────────────────────────────────────────────────────────
        screen.fill(DARK)

        # Camera feed (left side)
        if current_frame_surface:
            screen.blit(current_frame_surface, (20, 120))
            pygame.draw.rect(screen, GRAY, (20, 120, CAM_W, CAM_H), 2)

        # Live gesture label under camera
        draw_text(screen, f"Your hand: {GESTURE_LABEL.get(live_gesture, '...')}",
                  22, 20 + CAM_W // 2, 490, YELLOW, center=True)

        # ── Right panel ──────────────────────────────────────────────────────
        rx = 560  # right panel x start

        if state == "menu":
            draw_text(screen, "ROCK PAPER SCISSORS AI", 36, WIDTH // 2, 40, WHITE, center=True)
            draw_text(screen, f"Difficulty:  [1] Easy  [2] Medium  [3] Hard", 22, rx, 140, GRAY)
            diff_color = {"easy": GREEN, "medium": YELLOW, "hard": RED}[difficulty]
            draw_text(screen, f"► {difficulty.upper()}", 28, rx, 175, diff_color)
            draw_text(screen, f"Best of:  [B] Toggle", 22, rx, 230, GRAY)
            draw_text(screen, f"► Best of {best_of}", 28, rx, 265, BLUE)
            draw_text(screen, "SPACE  →  Start", 30, WIDTH // 2, 420, GREEN, center=True)

        elif state == "countdown":
            draw_text(screen, "GET READY!", 40, rx + 100, 180, WHITE, center=True)
            draw_text(screen, str(countdown_val) if countdown_val > 0 else "GO!",
                      100, rx + 100, 290, YELLOW, center=True)

        elif state == "detecting":
            draw_text(screen, "SHOW YOUR MOVE!", 36, rx + 100, 250, GREEN, center=True)

        elif state == "result":
            p_label = GESTURE_LABEL.get(detected_gesture, "?")
            a_label = GESTURE_LABEL.get(ai_move, "?")
            draw_text(screen, f"You:  {p_label}", 28, rx, 160, WHITE)
            draw_text(screen, f"AI:   {a_label}", 28, rx, 210, WHITE)

            if round_result == "player":
                draw_text(screen, "YOU WIN!", 50, rx + 100, 310, GREEN, center=True)
            elif round_result == "ai":
                draw_text(screen, "AI WINS!", 50, rx + 100, 310, RED, center=True)
            else:
                draw_text(screen, "DRAW!", 50, rx + 100, 310, YELLOW, center=True)

        elif state == "game_over":
            winner = "YOU WIN! 🎉" if game.player_score > game.ai_score else "AI WINS! 🤖"
            color = GREEN if game.player_score > game.ai_score else RED
            draw_text(screen, winner, 50, WIDTH // 2, 200, color, center=True)
            draw_text(screen, f"Final: {game.player_score} - {game.ai_score}", 36,
                      WIDTH // 2, 280, WHITE, center=True)
            draw_text(screen, "SPACE → Menu", 28, WIDTH // 2, 420, GRAY, center=True)

        # ── HUD (always visible) ─────────────────────────────────────────────
        if state not in ("menu",):
            status = game.get_status()
            hud = f"Round {status['round']}  |  You: {status['player_score']}  AI: {status['ai_score']}  |  Best of {status['best_of']}  |  {difficulty.upper()}"
            draw_text(screen, hud, 20, WIDTH // 2, 10, GRAY, center=True)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    run_game()