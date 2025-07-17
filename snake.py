import pygame
import random
import sys
import logging
import json
import os
from datetime import datetime

# Create logs directory before logging setup
try:
    os.makedirs('logs', exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create logs directory: {e}")

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/snake_game.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('snake_game')

# Initialize Pygame with error handling
try:
    pygame.init()
    logger.info("Pygame initialized successfully")
except pygame.error as e:
    logger.error(f"Failed to initialize Pygame: {e}")
    sys.exit(1)

# Move pygame-dependent globals after initialization
WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    logger.info(f"Display initialized successfully: {WIDTH}x{HEIGHT}")
except pygame.error as e:
    logger.error(f"Failed to initialize display mode ({WIDTH}x{HEIGHT}): {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error initializing display: {e}")
    sys.exit(1)

# Initialize clock with error handling
try:
    clock = pygame.time.Clock()
    logger.debug("Clock initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize clock: {e}")
    sys.exit(1)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.grow = False
        self.max_length = GRID_WIDTH * GRID_HEIGHT - 10  # Prevent memory overflow
        
    def move(self):
        head = self.positions[0]
        x, y = self.direction
        new_head = (head[0] + x, head[1] + y)
        
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or \
           new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or \
           new_head in self.positions:
            return False
            
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            
        return True
        
    def change_direction(self, direction):
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
            
    def eat(self):
        self.grow = True

class Food:
    def __init__(self):
        self.position = None
        self.randomize_position()
        
    def randomize_position(self, snake_positions=None):
        try:
            max_attempts = 1000  # Prevent infinite loop
            attempts = 0
            while attempts < max_attempts:
                new_position = (random.randint(0, GRID_WIDTH-1), 
                               random.randint(0, GRID_HEIGHT-1))
                
                if snake_positions is None or new_position not in snake_positions:
                    self.position = new_position
                    logger.debug(f"Food positioned at {new_position}")
                    return
                attempts += 1
            
            # If we can't find a free position, the game is essentially won
            logger.warning("No free position for food - game board full!")
            self.position = None
        except Exception as e:
            logger.error(f"Error randomizing food position: {e}")
            # Set a default position as fallback
            self.position = (0, 0)

def draw_text(surface, text, size, color, x, y):
    try:
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)
    except Exception as e:
        logger.error(f"Error drawing text '{text}': {e}")
        # Continue without crashing the game

def game_over_screen(screen, score):
    screen.fill(BLACK)
    draw_text(screen, f"Game Over! Score: {score}", 40, WHITE, WIDTH//2, HEIGHT//2 - 50)
    draw_text(screen, "Press SPACE to play again", 30, WHITE, WIDTH//2, HEIGHT//2 + 10)
    draw_text(screen, "Press ESC to quit", 30, WHITE, WIDTH//2, HEIGHT//2 + 50)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
    
    # This line was unreachable, removed redundant return

def save_high_score(score):
    """Save high score to file with error handling"""
    high_score_file = "high_score.json"
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(high_score_file) if os.path.dirname(high_score_file) else '.', exist_ok=True)
        
        # Load existing high score
        high_score = 0
        if os.path.exists(high_score_file):
            try:
                with open(high_score_file, 'r') as f:
                    data = json.load(f)
                    high_score = data.get('high_score', 0)
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not read high score file: {e}")
        
        # Update if new high score
        if score > high_score:
            with open(high_score_file, 'w') as f:
                json.dump({
                    'high_score': score,
                    'date': datetime.now().isoformat()
                }, f)
            logger.info(f"New high score saved: {score}")
            return True
        return False
    except Exception as e:
        logger.error(f"Error saving high score: {e}")
        return False

def load_high_score():
    """Load high score from file with error handling"""
    high_score_file = "high_score.json"
    try:
        if os.path.exists(high_score_file):
            with open(high_score_file, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except Exception as e:
        logger.warning(f"Could not load high score: {e}")
    return 0

def main():
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create logs directory: {e}")
    
    play_again = True
    
    while play_again:
        try:
            snake = Snake()
            food = Food()
            running = True
            score = 0
            high_score = load_high_score()
            logger.info("New game started")
            
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        play_again = False
                    elif event.type == pygame.KEYDOWN:
                        try:
                            if event.key == pygame.K_UP:
                                snake.change_direction((0, -1))
                                logger.debug("Direction changed: UP")
                            elif event.key == pygame.K_DOWN:
                                snake.change_direction((0, 1))
                                logger.debug("Direction changed: DOWN")
                            elif event.key == pygame.K_LEFT:
                                snake.change_direction((-1, 0))
                                logger.debug("Direction changed: LEFT")
                            elif event.key == pygame.K_RIGHT:
                                snake.change_direction((1, 0))
                                logger.debug("Direction changed: RIGHT")
                            elif event.key == pygame.K_ESCAPE:
                                running = False
                                play_again = False
                                logger.info("Game exited by user")
                        except Exception as e:
                            logger.error(f"Error handling key press: {e}")
                
                if not snake.move():
                    logger.info(f"Game over! Final score: {score}")
                    save_high_score(score)
                    play_again = game_over_screen(screen, score)
                    running = False
                    continue
                    
                if food.position is not None and snake.positions[0] == food.position:
                    snake.eat()
                    food.randomize_position(snake.positions)
                    score += 10
                    # Update high score display when new record is set
                    if score > high_score:
                        high_score = score
                    
                screen.fill(BLACK)
                
                for position in snake.positions:
                    rect = pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, GREEN, rect)
                    pygame.draw.rect(screen, BLACK, rect, 1)
                
                # Add null check for food.position before drawing
                if food.position is not None:
                    food_rect = pygame.Rect(food.position[0] * CELL_SIZE, 
                                           food.position[1] * CELL_SIZE,
                                           CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, RED, food_rect)
                
                draw_text(screen, f"Score: {score} | High Score: {high_score}", 30, WHITE, WIDTH//2, 30)
                
                pygame.display.flip()
                clock.tick(10)
            
        except Exception as e:
            logger.error(f"Error during game loop: {e}")
            # Try to show error screen
            try:
                screen.fill(BLACK)
                draw_text(screen, "Game Error!", 40, RED, WIDTH//2, HEIGHT//2 - 50)
                draw_text(screen, "Check logs for details", 30, WHITE, WIDTH//2, HEIGHT//2)
                draw_text(screen, "Press any key to exit", 25, WHITE, WIDTH//2, HEIGHT//2 + 50)
                pygame.display.flip()
                
                waiting = True
                while waiting:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                            waiting = False
                            play_again = False
            except:
                pass
                
    logger.info("Game session ended")
    pygame.quit()

if __name__ == "__main__":
    main()