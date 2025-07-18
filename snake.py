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
        try:
            # Check if snake has reached maximum safe length
            if len(self.positions) >= self.max_length:
                logger.warning(f"Snake reached maximum length limit: {self.max_length}")
                # Don't grow anymore to prevent memory issues
                return False
            elif len(self.positions) >= self.max_length * 0.9:
                # Warn when approaching limit
                logger.info(f"Snake approaching maximum length: {len(self.positions)}/{self.max_length}")
            
            self.grow = True
            return True
        except Exception as e:
            logger.error(f"Error in snake eat method: {e}")
            # Safe fallback - don't grow if there's an error
            return False

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
            
            # If we can't find a free position after max attempts
            logger.warning("No free position for food after max attempts")
            # Try to find any free position systematically
            if snake_positions:
                for x in range(GRID_WIDTH):
                    for y in range(GRID_HEIGHT):
                        if (x, y) not in snake_positions:
                            self.position = (x, y)
                            logger.info(f"Found alternative food position at {self.position}")
                            return
            # Game board is truly full
            logger.info("Game board full - player wins!")
            self.position = None
        except Exception as e:
            logger.error(f"Error randomizing food position: {e}")
            # Try to find a safe fallback position
            if snake_positions and (0, 0) not in snake_positions:
                self.position = (0, 0)
            else:
                # Find first available position
                for x in range(GRID_WIDTH):
                    for y in range(GRID_HEIGHT):
                        if snake_positions is None or (x, y) not in snake_positions:
                            self.position = (x, y)
                            return
                self.position = None

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

def flash_screen(surface, color, duration=100):
    """Create a brief flash effect on the screen"""
    try:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)  # Semi-transparent
        overlay.fill(color)
        surface.blit(overlay, (0, 0))
        pygame.display.flip()
        pygame.time.wait(duration)
    except Exception as e:
        logger.error(f"Error creating flash effect: {e}")

def game_over_screen(screen, score):
    screen.fill(BLACK)
    draw_text(screen, f"Game Over! Score: {score}", 40, WHITE, WIDTH//2, HEIGHT//2 - 50)
    draw_text(screen, "Press SPACE to play again", 30, WHITE, WIDTH//2, HEIGHT//2 + 10)
    draw_text(screen, "Press ESC to quit", 30, WHITE, WIDTH//2, HEIGHT//2 + 50)
    pygame.display.flip()
    
    waiting = True
    timeout_counter = 0
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        # Add timeout to prevent infinite loop (10 seconds)
        timeout_counter += 1
        pygame.time.wait(100)  # Wait 100ms
        if timeout_counter > 100:  # 10 seconds timeout
            logger.warning("Game over screen timeout - exiting")
            return False
    
    # Default return if somehow we exit the loop
    return False

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
    global screen
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
            paused = False
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
                            elif event.key == pygame.K_p:
                                paused = not paused
                                if paused:
                                    logger.info("Game paused")
                                else:
                                    logger.info("Game resumed")
                        except Exception as e:
                            logger.error(f"Error handling key press: {e}")
                
                # Skip game logic if paused
                if not paused:
                    if not snake.move():
                        logger.info(f"Game over! Final score: {score}")
                        save_high_score(score)
                        play_again = game_over_screen(screen, score)
                        running = False
                        continue
                    
                    if food.position is not None and snake.positions[0] == food.position:
                        if snake.eat():
                            food.randomize_position(snake.positions)
                            score += 10
                            # Flash effect when eating food
                            flash_screen(screen, WHITE, 50)
                            logger.info(f"Food eaten! Score: {score}")
                            # Update high score display when new record is set
                            if score > high_score:
                                high_score = score
                        else:
                            # Snake reached max length - player essentially won
                            logger.info("Snake reached maximum length - game complete!")
                            # Don't increment score when snake can't grow
                            # Set food position to None to indicate game completion
                            food.position = None
                    
                # Wrap rendering operations in error handling
                try:
                    # Check if screen is valid before rendering
                    if screen is None:
                        logger.error("Screen object is None, attempting to reinitialize")
                        try:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))
                            pygame.display.set_caption("Snake Game")
                        except Exception as e:
                            logger.critical(f"Cannot reinitialize display: {e}")
                            running = False
                            play_again = False
                            break
                    
                    screen.fill(BLACK)
                    
                    # Draw snake with error handling
                    for position in snake.positions:
                        try:
                            rect = pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE,
                                              CELL_SIZE, CELL_SIZE)
                            pygame.draw.rect(screen, GREEN, rect)
                            pygame.draw.rect(screen, BLACK, rect, 1)
                        except pygame.error as e:
                            logger.error(f"Error drawing snake segment at {position}: {e}")
                    
                    # Add null check for food.position before drawing
                    if food.position is not None:
                        try:
                            food_rect = pygame.Rect(food.position[0] * CELL_SIZE, 
                                                   food.position[1] * CELL_SIZE,
                                                   CELL_SIZE, CELL_SIZE)
                            pygame.draw.rect(screen, RED, food_rect)
                        except pygame.error as e:
                            logger.error(f"Error drawing food at {food.position}: {e}")
                    
                    draw_text(screen, f"Score: {score} | High Score: {high_score}", 30, WHITE, WIDTH//2, 30)
                    
                    # Display pause text if game is paused
                    if paused:
                        draw_text(screen, "PAUSED", 60, WHITE, WIDTH//2, HEIGHT//2)
                        draw_text(screen, "Press P to resume", 25, WHITE, WIDTH//2, HEIGHT//2 + 50)
                    
                    pygame.display.flip()
                except pygame.error as e:
                    logger.error(f"Critical rendering error: {e}")
                    # Try to recover by reinitializing display
                    try:
                        pygame.display.quit()
                        pygame.display.init()
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        pygame.display.set_caption("Snake Game")
                        logger.warning("Display reinitialized after rendering error")
                    except Exception as reinit_error:
                        logger.critical(f"Failed to reinitialize display: {reinit_error}")
                        running = False
                        play_again = False
                        # Exit immediately when display cannot be recovered
                        break
                except Exception as e:
                    logger.error(f"Unexpected rendering error: {e}")
                
                try:
                    # Use slower tick rate when paused to save CPU
                    if paused:
                        clock.tick(30)  # 30 FPS when paused (just for UI updates)
                    else:
                        clock.tick(10)  # Normal game speed
                except Exception as e:
                    logger.error(f"Clock tick error: {e}")
                    # Try to limit frame rate manually
                    try:
                        pygame.time.wait(100)  # Wait 100ms (10 FPS)
                    except:
                        pass  # Continue without any frame rate limiting
            
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