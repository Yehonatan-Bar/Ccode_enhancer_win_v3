import pygame
import random
import sys
import logging
import json
import os
from datetime import datetime
from snake_visuals import VisualEffects, Theme

# Setup logging
log_dir = '../../logs'
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(feature)s.%(component)s] - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'snake_game.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('snake_game')

# Read logging configuration
try:
    with open('../../logging.json', 'r') as f:
        log_config = json.load(f)
        if log_config.get('enabled'):
            logger.info("Logging enabled", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
except Exception as e:
    logger.warning(f"Could not load logging config: {e}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})

# Initialize Pygame with error handling
try:
    pygame.init()
    logger.info("Pygame initialized successfully", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
except pygame.error as e:
    logger.error(f"Failed to initialize Pygame: {e}", extra={'feature': 'ERROR_HANDLING', 'component': 'COMPONENTS'})
    sys.exit(1)

# Constants
WIDTH = 800
HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE
FPS = 10

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.grow = False
        self.max_length = GRID_WIDTH * GRID_HEIGHT - 10  # Prevent memory overflow
        logger.info("Snake initialized", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
        
    def move(self):
        head = self.positions[0]
        x, y = self.direction
        new_head = (head[0] + x, head[1] + y)
        
        # Check collision with walls
        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or \
           new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            logger.info("Snake hit wall", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
            return False
            
        # Check collision with self
        if new_head in self.positions:
            logger.info("Snake hit itself", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
            return False
            
        self.positions.insert(0, new_head)
        
        if not self.grow:
            self.positions.pop()
        else:
            self.grow = False
            logger.debug(f"Snake grew to length {len(self.positions)}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
            
        return True
        
    def change_direction(self, direction):
        # Prevent snake from going back into itself
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
            logger.debug(f"Direction changed to {direction}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
            
    def eat(self):
        if len(self.positions) < self.max_length:
            self.grow = True

class Food:
    def __init__(self):
        self.position = None
        self.randomize_position()
        logger.info("Food initialized", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
        
    def randomize_position(self, snake_positions=None):
        try:
            max_attempts = 1000  # Prevent infinite loop
            attempts = 0
            while attempts < max_attempts:
                new_position = (random.randint(0, GRID_WIDTH-1), 
                               random.randint(0, GRID_HEIGHT-1))
                
                if snake_positions is None or new_position not in snake_positions:
                    self.position = new_position
                    logger.debug(f"Food positioned at {new_position}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
                    return
                attempts += 1
            
            # If we can't find a free position, the game is essentially won
            logger.warning("No free position for food - game board full!", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
            self.position = None
        except Exception as e:
            logger.error(f"Error randomizing food position: {e}", extra={'feature': 'ERROR_HANDLING', 'component': 'COMPONENTS'})
            # Set a default position as fallback
            self.position = (0, 0)

class GameState:
    def __init__(self):
        self.snake = None
        self.food = None
        self.score = 0
        self.high_score = self.load_high_score()
        self.running = False
        self.game_over = False
        self.in_menu = True
        self.visual_effects = None
        self.current_theme_index = 0
        self.themes = list(Theme)
        logger.info("GameState initialized", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
        
    def new_game(self):
        self.snake = Snake()
        self.food = Food()
        self.score = 0
        self.running = True
        self.game_over = False
        self.in_menu = False
        logger.info("New game started", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
        
    def update(self):
        if not self.running or self.game_over:
            return
            
        if not self.snake.move():
            self.game_over = True
            self.save_high_score()
            logger.info(f"Game over! Final score: {self.score}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
            return
            
        # Check if snake ate food
        if self.food.position is not None and self.snake.positions[0] == self.food.position:
            self.snake.eat()
            self.food.randomize_position(self.snake.positions)
            self.score += 10
            
            # Create particle effect
            if self.visual_effects:
                self.visual_effects.create_eat_particles(self.snake.positions[0])
            
            # Update high score display when new record is set
            if self.score > self.high_score:
                self.high_score = self.score
                
            logger.info(f"Food eaten! Score: {self.score}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
    
    def change_theme(self):
        self.current_theme_index = (self.current_theme_index + 1) % len(self.themes)
        new_theme = self.themes[self.current_theme_index]
        if self.visual_effects:
            self.visual_effects.set_theme(new_theme)
        logger.info(f"Theme changed to {new_theme.value}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
        
    def save_high_score(self):
        """Save high score to file with error handling"""
        high_score_file = "games/snake/high_score.json"
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(high_score_file), exist_ok=True)
            
            # Update if new high score
            if self.score > self.high_score:
                with open(high_score_file, 'w') as f:
                    json.dump({
                        'high_score': self.score,
                        'date': datetime.now().isoformat()
                    }, f)
                logger.info(f"New high score saved: {self.score}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving high score: {e}", extra={'feature': 'ERROR_HANDLING', 'component': 'COMPONENTS'})
            return False
    
    def load_high_score(self):
        """Load high score from file with error handling"""
        high_score_file = "games/snake/high_score.json"
        try:
            if os.path.exists(high_score_file):
                with open(high_score_file, 'r') as f:
                    data = json.load(f)
                    score = data.get('high_score', 0)
                    logger.info(f"High score loaded: {score}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
                    return score
        except Exception as e:
            logger.warning(f"Could not load high score: {e}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
        return 0

def handle_input(game_state, event):
    """Handle user input"""
    try:
        if event.type == pygame.KEYDOWN:
            if game_state.in_menu:
                if event.key == pygame.K_SPACE:
                    game_state.new_game()
                elif event.key == pygame.K_t:
                    game_state.change_theme()
                elif event.key == pygame.K_ESCAPE:
                    return False
            elif game_state.game_over:
                if event.key == pygame.K_SPACE:
                    game_state.new_game()
                elif event.key == pygame.K_t:
                    game_state.change_theme()
                elif event.key == pygame.K_ESCAPE:
                    game_state.in_menu = True
                    game_state.game_over = False
            else:
                # Game controls
                if event.key == pygame.K_UP and game_state.snake.direction != (0, 1):
                    game_state.snake.change_direction((0, -1))
                elif event.key == pygame.K_DOWN and game_state.snake.direction != (0, -1):
                    game_state.snake.change_direction((0, 1))
                elif event.key == pygame.K_LEFT and game_state.snake.direction != (1, 0):
                    game_state.snake.change_direction((-1, 0))
                elif event.key == pygame.K_RIGHT and game_state.snake.direction != (-1, 0):
                    game_state.snake.change_direction((1, 0))
                elif event.key == pygame.K_ESCAPE:
                    game_state.running = False
                    game_state.in_menu = True
    except Exception as e:
        logger.error(f"Error handling input: {e}", extra={'feature': 'ERROR_HANDLING', 'component': 'COMPONENTS'})
    
    return True

def main():
    """Main game loop"""
    try:
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('games/snake', exist_ok=True)
    except Exception as e:
        logger.warning(f"Could not create directories: {e}", extra={'feature': 'ERROR_HANDLING', 'component': 'COMPONENTS'})
    
    # Initialize display
    try:
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game - Enhanced Edition")
        logger.info(f"Display initialized: {WIDTH}x{HEIGHT}", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
    except pygame.error as e:
        logger.error(f"Failed to initialize display: {e}", extra={'feature': 'ERROR_HANDLING', 'component': 'COMPONENTS'})
        sys.exit(1)
    
    # Initialize clock
    clock = pygame.time.Clock()
    
    # Create game state and visual effects
    game_state = GameState()
    game_state.visual_effects = VisualEffects(WIDTH, HEIGHT, CELL_SIZE)
    
    # Main game loop
    running = True
    while running:
        try:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                else:
                    if not handle_input(game_state, event):
                        running = False
            
            # Update game state
            if game_state.running and not game_state.game_over:
                game_state.update()
            
            # Update visual effects
            game_state.visual_effects.update_particles()
            
            # Render
            if game_state.in_menu:
                game_state.visual_effects.draw_main_menu(screen)
            else:
                # Draw background
                game_state.visual_effects.draw_gradient_background(screen)
                game_state.visual_effects.draw_grid_lines(screen)
                
                # Draw game elements
                if game_state.snake:
                    game_state.visual_effects.draw_snake(screen, game_state.snake.positions)
                
                if game_state.food and game_state.food.position:
                    game_state.visual_effects.draw_food(screen, game_state.food.position)
                
                # Draw particles
                game_state.visual_effects.draw_particles(screen)
                
                # Draw UI
                game_state.visual_effects.draw_score_display(screen, game_state.score, game_state.high_score)
                
                # Draw game over screen if needed
                if game_state.game_over:
                    game_state.visual_effects.draw_game_over_screen(screen, game_state.score, game_state.high_score)
            
            # Update display
            pygame.display.flip()
            clock.tick(FPS)
            
        except Exception as e:
            logger.error(f"Error in game loop: {e}", extra={'feature': 'ERROR_HANDLING', 'component': 'COMPONENTS'})
            # Try to show error screen
            try:
                screen.fill((0, 0, 0))
                if game_state.visual_effects and game_state.visual_effects.title_font:
                    error_text = game_state.visual_effects.title_font.render("Game Error!", True, (255, 0, 0))
                    screen.blit(error_text, (WIDTH//2 - error_text.get_width()//2, HEIGHT//2))
                pygame.display.flip()
                pygame.time.wait(2000)
            except:
                pass
            running = False
    
    logger.info("Game session ended", extra={'feature': 'SNAKE_GAME', 'component': 'COMPONENTS'})
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()