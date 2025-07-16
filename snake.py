import pygame
import random
import sys

pygame.init()

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
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
        
    def randomize_position(self):
        self.position = (random.randint(0, GRID_WIDTH-1), 
                        random.randint(0, GRID_HEIGHT-1))

def main():
    snake = Snake()
    food = Food()
    running = True
    score = 0
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
            print(f"Game Over! Score: {score}")
            pygame.quit()
            sys.exit()
            
        if snake.positions[0] == food.position:
            snake.eat()
            food.randomize_position()
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
        
        pygame.display.flip()
        clock.tick(10)
        
    pygame.quit()

if __name__ == "__main__":
    main()