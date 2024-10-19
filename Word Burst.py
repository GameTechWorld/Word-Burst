import pygame
import random
import requests
import time

# Function to fetch random words from the Random Word API with a specific length filter
def get_random_words(count=100, word_length=5, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        try:
            url = "https://random-word-api.herokuapp.com/word?number=" + str(count * 2)  # Fetch more words
            response = requests.get(url)
            
            if response.status_code == 200:
                words = response.json()
                # Filter words based on the specified length
                filtered_words = [word for word in words if len(word) == word_length]
                return filtered_words[:count]  # Return only the requested count
            else:
                print("Error fetching words:", response.text)
                attempts += 1
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            attempts += 1
            time.sleep(1)  # Wait a bit before retrying
    return []

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Word Burst")

# Colors
LIGHT_GRAY = (200, 200, 200)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
NAVY = (70, 130, 180)

# Font
font = pygame.font.Font(None, 36)

# Fetch random words for the game with a specific length of 5
word_list = get_random_words(20, word_length=8)  # Fetch 20 random words of length 8

# Check if the word_list is empty and provide a fallback
if not word_list:
    print("No valid words fetched. Using default word list.")
    word_list = ["hello", "world", "python", "game", "typing", "fun", "arcade"]  # Default words

# Balloon class
class Balloon:
    def __init__(self, word, speed, color):
        self.word = word
        self.x = random.randint(50, SCREEN_WIDTH - 100)
        self.y = 80
        self.original_speed = speed
        self.speed = speed
        self.color = color

    def draw(self):
        text_surface = font.render(self.word, True, BLACK)
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        pygame.draw.circle(screen, self.color, (self.x, self.y), 35)
        screen.blit(text_surface, text_rect)

    def update(self):
        self.y += self.speed

# Button class
class Button:
    def __init__(self, text, x, y, width, height, color, hover_color):
        self.text = text
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color

    def draw(self):
        mouse = pygame.mouse.get_pos()
        if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
            pygame.draw.rect(screen, self.hover_color, (self.x, self.y, self.width, self.height), border_radius=15)
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=15)

        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(text_surface, text_rect)

    def is_clicked(self):
        mouse = pygame.mouse.get_pos()
        return self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height

# Function to reset game variables
def reset_game():
    global score, game_over, balloons, current_word, spawn_timer, slow_down, slow_down_timer
    score = 0
    game_over = False
    balloons = []
    current_word = ""
    spawn_timer = 0
    slow_down = False
    slow_down_timer = 0

# Function to draw a rounded rectangle
def draw_rounded_rect(surface, color, rect, radius):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

# Game variables
clock = pygame.time.Clock()
score = 0
slow_down_timer = 0
game_over = False
balloons = []
current_word = ""
spawn_timer = 0
paused = False
slow_down = False

# High score management
high_score_file = "high_score.txt"
try:
    with open(high_score_file, "r") as f:
        high_score = int(f.read())
except FileNotFoundError:
    high_score = 0
    with open(high_score_file, "w") as f:
        f.write(str(high_score))

# Create pause button
button_width = 100
button_height = 30
padding = 10
pause_button = Button("Pause", SCREEN_WIDTH - button_width - padding, padding, button_width, button_height, GREEN, (0, 200, 0))

# Navigation bar height
nav_bar_height = 50

# Margins
MARGIN = 20
SIDE_MARGIN = 30

# Input box border color
input_box_border_color = BLACK

# Timer for input box border color change
input_box_timer = 0

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pause_button.is_clicked():
                paused = not paused
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_r:
                    reset_game()
            elif not paused:
                if event.unicode.isalnum():
                    current_word += event.unicode
                if event.key == pygame.K_BACKSPACE:
                    current_word = current_word[:-1]
                if event.key == pygame.K_RETURN:
                    if current_word:
                        matched = False
                        for balloon in balloons:
                            if balloon.word == current_word:
                                matched = True
                                score += len(balloon.word)
                                balloons.remove(balloon)
                                current_word = ""
                                if balloon.color == BLUE:
                                    slow_down = True
                                    slow_down_timer = time.time()
                                elif balloon.color == YELLOW:
                                    for cleared_balloon in balloons:
                                        score += len(cleared_balloon.word)
                                    balloons.clear()
                                break
                        if not matched:
                            input_box_border_color = RED
                            input_box_timer = time.time() + 1
                            current_word = ""

    if not game_over and not paused:
        spawn_timer += 1
        if spawn_timer > 150:
            if random.random() < 0.125:
                balloons.append(Balloon(random.choice(word_list), 0.5 + (score // 100), BLUE))
            elif random.random() < 0.0714:
                balloons.append(Balloon(random.choice(word_list), 0.5 + (score // 100), YELLOW))
            else:
                balloons.append(Balloon(random.choice(word_list), 0.5 + (score // 100), RED))
            spawn_timer = 0

        for balloon in balloons:
            if slow_down:
                balloon.speed = 0.1
            else:
                balloon.speed = balloon.original_speed
            balloon.update()
            if balloon.y > SCREEN_HEIGHT - 30:
                game_over = True
            if (balloon.x > 0 and balloon.x < SCREEN_WIDTH and
                    balloon.y + 30 > SCREEN_HEIGHT - nav_bar_height and balloon.y - 30 < SCREEN_HEIGHT):
                game_over = True

        if slow_down and time.time() > slow_down_timer + 3:
            slow_down = False

    screen.fill(WHITE)

    pygame.draw.rect(screen, NAVY, (0, 0, SCREEN_WIDTH, nav_bar_height))

    score_surface = font.render("Score: " + str(score), True, WHITE)
    screen.blit(score_surface, (10, 10))

    high_score_surface = font.render("High Score: " + str(high_score), True, WHITE)
    screen.blit(high_score_surface, (SCREEN_WIDTH // 2 - high_score_surface.get_width() // 2, 10))

    pause_button.draw()

    for balloon in balloons:
        balloon.draw()

    if game_over:
        overlay_color = (0, 0, 0, 128)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(overlay_color)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        game_over_background_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 100)
        draw_rounded_rect(screen, BLACK, game_over_background_rect, 20)

        if score > high_score:
            high_score = score
            with open(high_score_file, "w") as f:
                f.write(str(high_score))
        game_over_surface = font.render("""Game Over! Press R to Restart""", True, RED)
        game_over_rect = game_over_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(game_over_surface, game_over_rect)

    if paused:
        overlay_color = (0, 0, 0, 128)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(overlay_color)
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        paused_background_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 50, 400, 100)
        draw_rounded_rect(screen, BLACK, paused_background_rect, 20)

        paused_surface = font .render("Paused. Press again to Resume", True, RED)
        paused_rect = paused_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(paused_surface, paused_rect)

    text_surface = font.render(current_word, True, BLACK)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - nav_bar_height // 2 - MARGIN))

    rounded_rect = pygame.Rect(SIDE_MARGIN, SCREEN_HEIGHT - nav_bar_height - MARGIN, SCREEN_WIDTH - 2 * SIDE_MARGIN, nav_bar_height)
    draw_rounded_rect(screen, LIGHT_GRAY, rounded_rect, 10)

    pygame.draw.rect(screen, input_box_border_color, rounded_rect, 2, border_radius=10)

    screen.blit(text_surface, text_rect)

    pygame.display.flip()
    clock.tick(60)
