import pygame
import random
import sys
import logging
import json
import os


# Setup logging based on configuration
def setup_logging():
    try:
        # Read logging configuration
        with open('logging.json', 'r') as't exist
        log_dir = log_config.get('output', {}).get('destination', './logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        return logging.getLogger('snake_game')
    except Exception as e:
        # Fallback if configuration fails
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger('snake_game')
        logger.error(f"Failed to load logging configuration: {e}")

# Initialize logger
logger = setup_logging()

# Initialize pygaadd-error-handling-snake-game] Pygame initialized successfully")
except pygame.error as e:
    logger.error(f"[COMMIT: add-error-handling-snake-game] Failed to initialize pygame: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"[COMMIT: add-error-handling-snake-game] Unexpected error during pygame initialization: {e}")
    sys.exit(1)

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize display with error handling
try:
     = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
    logger.info(f"[COMMIT: add-error-handling-snake-game] Display initialized: {WIDTH}x{HEIGHT}")
except pygame.error as e:
    logger.error(f"[COMMIT: add-error-handling-snake-game] Failed to create display: {e}")
    pygame.quit()
    sys.exit(1)
except Exception as e:
    logger.error(f"[COMMIT: add-error-handling-snake-game] Unexpected error creating display: {e}")
    pygame.quit()
    sys.exit(1)
    
# Initialize clock with error handling
try:
    clock = pygame.time.Clock()
    logger.info("[COMMIT: add-error-handling-snake-game] Clock initialized")
except Exception as e:
    logger.error(f"[COMMIT: add-error-handling-snake-game] Failed to create clock: {e}")
    pygame.quit()
    sys.exit(1)

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.grow = False
        
    def move(self):
        try:
            head = self.positions[0]
            x, y = self.direction
            new_head = (head[0] + x, head[1] + y)
            
            if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or \
               new_head[1] < 0 or new_head[1] >= GRID_HEIGHT or \
               new_head in self.positions:
                logger.debug(f"[COMMIT: add-error-handling-snake-game] Snake collision detected at position {new_head}")
                return False
                
            self.positions.insert(0, new_head)
                logger.debug("[COMMIT: add-error-handling-snake-game] Snake grew by one segment")
                
            return True
        except Exception as e:
            logger.error(f"[COMMIT: add-error-handling-snake-game] Error during snake movement: {e}")
            return False
        
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
        while True:
            new_position = (random.randint(0, GRID_WIDTH-1), 
                           random.randint(0, GRID_HEIGHT-1))
            
            if snake_positions is None or new_position not in snake_positions:
                self.position = new_position
                return

def draw_text(surface, text, size, color, x, y):
    except pygame.error as e:
        logger.error(f"[COMMIT: add-error-handling-snake-game] Font rendering error: {e}")
    except Exception as e:
        logger.error(f"[COMMIT: add-error-handling-snake-game] Unexpected error drawing text: {e}")

def game_over_screen(screen, score):
    try:
        screen.fill(BLACK)
        draw_text(screen, f"Game Over! Score: {score}", 40, WHITE, WIDTH//2, HEIGHT//2 - 50)
        draw_text(screen, "Press SPACE to play again", 30, WHITE, WIDTH//2, HEIGHT//2 + 10)
        draw_text(screen, "Press ESC to quit", 30, WHITE, WIDTH//2, HEIGHT//2 + 50)
        pygame.display.flip()
        logger.info(f"[COMMIT: add-error-handling-snake-game] Game over with score: {score}")
        
        waiting = True
        while waiting:
                logger.error(f"[COMMIT: add-error-handling-snake-game] Error processing game over events: {e}")
                return False
        
        return False
    except Exception as e:
        logger.error(f"[COMMIT: add-error-handling-snake-game] Error in game over screen: {e}")
        return False

def main():
    try:
        logger.info("[COMMIT: add-error-handling-snake-game] Snake game started")
        play_again = True
        games_played = 0
        
        while play_again:
                food = Food()
                running = True
                score = 0
                frame_count = 0
                
                while running:
                    try:
                        # Event handling with error handling
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                logger.info("[COMMIT: add-error-handling-snake-game] Quit event received")
                                running = False
                                play_again = False
                            elif event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_UP:
                                    snake.change_direction((0, -1))
                                elif event.key == pygame.K_DOWN:
                                    snake.change_direction((0, 1))
                        logger.error(f"[COMMIT: add-error-handling-snake-game] Error processing events: {e}")
                        continue
                    
                    # Game logic with error handling
                    try:
                        if not snake.move():
                            play_again = game_over_screen(screen, score)
                            running = False
                            continue
                            
                        if snake.positions[0] == food.position:
                            snake.eat()d eaten. Score: {score}")
                    except Exception as e:
                        logger.error(f"[COMMIT: add-error-handling-snake-game] Error in game logic: {e}")
                        running = False
                        continue
                    
                    # Rendering with error handling
                    try:
                        screen.fill(BLACK)
                        
                        # Draw snake
                        for position in snake.positions:
                            rect = pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE,
                                              CELL_SIZE, CELL_SIZE)
                            pygame.draw.rect(screen, GREEN, rect)
                        # Draw score
                        draw_text(screen, f"Score: {score}", 30, WHITE, WIDTH//2, 30)
                        
                        pygame.display.flip()
                    except pygame.error as e:
                        logger.error(f"[COMMIT: add-error-handling-snake-game] Rendering error: {e}")
                        running = False
                        continue
                    except Exception as e:
                        logger.error(f"[COMMIT: add-error-handling-snake-game] Unexpected rendering error: {e}")
                        running = False
                        continue
                    
                    # Frame rate control with error handling
                    try:
                        clock.tick(10)
                        frame_count += 1
                        
                        # Log performance metrics every 100 frames
                        if frame_count % 100 == 0:
                            fps = clock.get_fps()
                            logger.debug(f"[COMMIT: add-error-handling-snake-game] FPS: {fps:.2f}")
                    except Exception as e:
                        logger.error(f"[COMMIT: add-error-handling-snake-game] Clock error: {e}")
                
            except Exception as e:
                logger.error(f"[COMMIT: add-error-handling-snake-game] Game loop error: {e}")
                play_again = False
        
        logger.info(f"[COMMIT: add-error-handling-snake-game] Game ended. Total games played: {games_played}")
        
    except Exception as e:
        logger.error(f"[COMMIT: add-error-handling-snake-game] Fatal error in main: {e}")
    finally:
        try:
            pygame.quit()
            logger.info("[COMMIT: add-error-handling-snake-game] Pygame shut down successfully")
        except Exception as e:
            logger.error(f"[COMMIT: add-error-handling-snake-game] Error during pygame shutdown: {e}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("[COMMIT: add-error-handling-snake-game] Game interrupted by user")
        pygame.quit()
        logger.error(f"[COMMIT: add-error-handling-snake-game] Unhandled exception: {e}")
        pygame.quit()
        sys.exit(1)