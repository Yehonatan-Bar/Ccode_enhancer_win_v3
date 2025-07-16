import pygame
import random
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    pygame.init()
except pygame.error as e:
    logging.error(f"Failed to initialize pygame: {e}")
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

try:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake Game")
except pygame.error as e:
    logging.error(f"Failed to create display: {e}")
    pygame.quit()
    sys.exit(1)
    
clock = pygame.time.Clock()

class Snake:
    def __init__(self):
        self.positions = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.grow = False
        
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
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            new_position = (random.randint(0, GRID_WIDTH-1), 
                           random.randint(0, GRID_HEIGHT-1))
            
            if snake_positions is None or new_position not in snake_positions:
                self.position = new_position
                return
            
            attempts += 1
        
        logging.warning("Could not find valid food position after {} attempts".format(max_attempts))
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if snake_positions is None or (x, y) not in snake_positions:
                    self.position = (x, y)
                    return

def draw_text(surface, text, size, color, x, y):
    try:
        font = pygame.font.Font(None, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.center = (x, y)
        surface.blit(text_surface, text_rect)
    except pygame.error as e:
        logging.error(f"Failed to render text: {e}")

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
    
    return False

def main():
    play_again = True
    
    while play_again:
        snake = Snake()
        food = Food()
        running = True
        score = 0
        
        while running:
            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        play_again = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP:
                            snake.change_direction((0, -1))
                        elif event.key == pygame.K_DOWN:
                            snake.change_direction((0, 1))
                        elif event.key == pygame.K_LEFT:
                            snake.change_direction((-1, 0))
                        elif event.key == pygame.K_RIGHT:
                            snake.change_direction((1, 0))
                
                if not snake.move():
                    play_again = game_over_screen(screen, score)
                    running = False
                    continue
                    
                if snake.positions[0] == food.position:
                    snake.eat()
                    food.randomize_position(snake.positions)
                    score += 10
                    
                screen.fill(BLACK)
                
                for position in snake.positions:
                    rect = pygame.Rect(position[0] * CELL_SIZE, position[1] * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(screen, GREEN, rect)
                    pygame.draw.rect(screen, BLACK, rect, 1)
                    
                food_rect = pygame.Rect(food.position[0] * CELL_SIZE, 
                                       food.position[1] * CELL_SIZE,
                                       CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, RED, food_rect)
                
                draw_text(screen, f"Score: {score}", 30, WHITE, WIDTH//2, 30)
                
                pygame.display.flip()
                clock.tick(10)
                
            except pygame.error as e:
                logging.error(f"Game loop error: {e}")
                running = False
                play_again = False
        
    pygame.quit()
    logging.info("Game terminated successfully")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Game interrupted by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        try:
            pygame.quit()
        except:
            pass
        logging.info("Game shutdown complete")