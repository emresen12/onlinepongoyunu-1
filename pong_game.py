import json
import pygame
import sys
import socket
import threading

# Pygame başlat
pygame.init()

# Tam ekran mod
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = SCREEN.get_size()
pygame.display.set_caption("Pong - Glow Border Edition")

# Renkler
WHITE = (255, 255, 255)
BLACK = (10, 10, 30)

LEFT_PADDLE_COLOR = (243, 6, 6)
RIGHT_PADDLE_COLOR = (243, 6, 6)
LEFT_GLOW = (255, 0, 0)
RIGHT_GLOW = (255, 0, 0)
BORDER_COLOR = (0, 0, 255)

# FPS kontrolü
clock = pygame.time.Clock()
FPS = 60

# Raket boyutu ve hızı
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 100
PADDLE_SPEED = 10

# Top boyutu ve hızı
BALL_SIZE = 20
BALL_SPEED_X = 10
BALL_SPEED_Y = 10

# Raket pozisyonları
left_paddle = pygame.Rect(10, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
right_paddle = pygame.Rect(WIDTH - 20, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)

# Top pozisyonu
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Skorlar
left_score = 0
right_score = 0
font = pygame.font.SysFont("Arial", 36)

# --- ONLINE İÇİN EKLENENLER ---

# Server bilgileri (Buraya server IP adresini yaz)
SERVER_IP = "127.0.0.1"  # Örnek localhost, gerçek IP ile değiştir
SERVER_PORT = 12345

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((SERVER_IP, SERVER_PORT))
except Exception as e:
    print("Servera bağlanılamadı:", e)
    pygame.quit()
    sys.exit()

# Karşı raketin pozisyonunu güncellemek için değişken
opponent_paddle_y = HEIGHT // 2 - PADDLE_HEIGHT // 2

def send_position(y):
    try:
        data = json.dumps({"paddle_y": y}).encode()
        client_socket.sendall(data)
    except:
        pass

def receive_data():
    global opponent_paddle_y
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            obj = json.loads(data.decode())
            opponent_paddle_y = obj.get("paddle_y", opponent_paddle_y)
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()

# ------------------------------------

def reset_ball():
    global BALL_SPEED_X, BALL_SPEED_Y
    ball.center = (WIDTH // 2, HEIGHT // 2)
    BALL_SPEED_X *= -1
    BALL_SPEED_Y *= -1

def draw_glow_rect(surface, rect, color):
    for i in range(6, 0, -1):
        glow_rect = rect.inflate(i * 4, i * 4)
        alpha = max(20, 255 - i * 40)
        glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        glow_surf.fill((*color, alpha))
        surface.blit(glow_surf, glow_rect.topleft)
    pygame.draw.rect(surface, color, rect)

def draw_glow_paddle(surface, rect, color, glow_color):
    draw_glow_rect(surface, rect, glow_color)
    pygame.draw.rect(surface, color, rect)

def draw_glow_border(surface, color, thickness=4):
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, WIDTH, thickness))  # üst
    pygame.draw.rect(surface, color, pygame.Rect(0, HEIGHT - thickness, WIDTH, thickness))  # alt
    pygame.draw.rect(surface, color, pygame.Rect(0, 0, thickness, HEIGHT))  # sol
    pygame.draw.rect(surface, color, pygame.Rect(WIDTH - thickness, 0, thickness, HEIGHT))  # sağ

    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(surface, color, pygame.Rect(WIDTH // 2 - 2, y, 4, 20))

# Oyun döngüsü
running = True
while running:
    clock.tick(FPS)

    # Olaylar
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # ESC ile çık
                running = False

    # Tuşlar
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and left_paddle.top > 0:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s] and left_paddle.bottom < HEIGHT:
        left_paddle.y += PADDLE_SPEED

    # --- ONLINE: Sağ raketin pozisyonunu server'dan alıyoruz ---
    right_paddle.y = opponent_paddle_y

    # Kendi raket pozisyonunu server'a gönder
    send_position(left_paddle.y)

    # Top hareketi
    ball.x += BALL_SPEED_X
    ball.y += BALL_SPEED_Y

    # Üst-alt sınırlar
    if ball.top <= 0 or ball.bottom >= HEIGHT:
        BALL_SPEED_Y *= -1

    # Raket çarpışmaları
    if ball.colliderect(left_paddle) or ball.colliderect(right_paddle):
        BALL_SPEED_X *= -1

    # Skor kontrolü
    if ball.left <= 0:
        right_score += 1
        reset_ball()
    if ball.right >= WIDTH:
        left_score += 1
        reset_ball()

    file = "keep_score.json"
    if left_score >= 3 or right_score >= 3:
        winner = "Left Player" if left_score >= 10 else "Right Player"
        with open(file, "r", encoding="utf-8") as f:
            scores = json.load(f)
        if winner == "Left Player":
            scores["player1"] += 1
        elif winner == "Right Player":
            scores["player2"] += 1
        with open(file, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=4)

        SCREEN.fill(BLACK)
        font_big = pygame.font.SysFont("Arial", 72)
        winner_text = font_big.render(f"Winner: {winner}", True, WHITE)
        SCREEN.blit(winner_text,
                    (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - winner_text.get_height() // 2))
        pygame.display.flip()

        # 3 saniye bekle
        pygame.time.delay(1000)
        pygame.quit()
        sys.exit()

    # Ekranı temizle
    SCREEN.fill(BLACK)

    draw_glow_border(SCREEN, BORDER_COLOR)
    draw_glow_paddle(SCREEN, left_paddle, LEFT_PADDLE_COLOR, LEFT_GLOW)
    draw_glow_paddle(SCREEN, right_paddle, RIGHT_PADDLE_COLOR, RIGHT_GLOW)
    pygame.draw.ellipse(SCREEN, (255, 255, 0), ball)

    left_text = font.render(f"{left_score}", True, WHITE)
    right_text = font.render(f"{right_score}", True, WHITE)
    SCREEN.blit(left_text, (WIDTH // 4, 20))
    SCREEN.blit(right_text, (WIDTH * 3 // 4, 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
