import pygame
import math
import random
import logging
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from enum import Enum

logger = logging.getLogger('snake_game.visuals')

class Theme(Enum):
    CLASSIC = "classic"
    NEON = "neon"
    NATURE = "nature"
    OCEAN = "ocean"
    SUNSET = "sunset"

@dataclass
class ColorScheme:
    background_start: Tuple[int, int, int]
    background_end: Tuple[int, int, int]
    snake_head: Tuple[int, int, int]
    snake_body: Tuple[int, int, int]
    snake_outline: Tuple[int, int, int]
    food: Tuple[int, int, int]
    food_glow: Tuple[int, int, int]
    text: Tuple[int, int, int]
    text_shadow: Tuple[int, int, int]
    particle: Tuple[int, int, int]

THEMES: Dict[Theme, ColorScheme] = {
    Theme.CLASSIC: ColorScheme(
        background_start=(20, 20, 30),
        background_end=(40, 40, 60),
        snake_head=(0, 255, 0),
        snake_body=(0, 200, 0),
        snake_outline=(0, 150, 0),
        food=(255, 0, 0),
        food_glow=(255, 100, 100),
        text=(255, 255, 255),
        text_shadow=(100, 100, 100),
        particle=(255, 200, 0)
    ),
    Theme.NEON: ColorScheme(
        background_start=(10, 0, 20),
        background_end=(30, 0, 50),
        snake_head=(0, 255, 255),
        snake_body=(0, 200, 255),
        snake_outline=(255, 0, 255),
        food=(255, 0, 255),
        food_glow=(255, 100, 255),
        text=(255, 255, 255),
        text_shadow=(150, 0, 150),
        particle=(255, 255, 0)
    ),
    Theme.NATURE: ColorScheme(
        background_start=(34, 83, 41),
        background_end=(53, 130, 64),
        snake_head=(139, 69, 19),
        snake_body=(160, 82, 45),
        snake_outline=(101, 67, 33),
        food=(255, 140, 0),
        food_glow=(255, 165, 0),
        text=(255, 255, 255),
        text_shadow=(0, 100, 0),
        particle=(255, 215, 0)
    ),
    Theme.OCEAN: ColorScheme(
        background_start=(0, 50, 100),
        background_end=(0, 100, 150),
        snake_head=(64, 224, 208),
        snake_body=(72, 209, 204),
        snake_outline=(0, 139, 139),
        food=(255, 99, 71),
        food_glow=(255, 127, 80),
        text=(255, 255, 255),
        text_shadow=(0, 50, 100),
        particle=(255, 218, 185)
    ),
    Theme.SUNSET: ColorScheme(
        background_start=(255, 94, 77),
        background_end=(255, 154, 0),
        snake_head=(138, 43, 226),
        snake_body=(147, 112, 219),
        snake_outline=(75, 0, 130),
        food=(255, 255, 0),
        food_glow=(255, 255, 100),
        text=(255, 255, 255),
        text_shadow=(139, 0, 0),
        particle=(255, 20, 147)
    )
}

class Particle:
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 1.0
        self.decay = random.uniform(0.01, 0.03)
        self.size = random.randint(3, 8)
        self.color = color
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.vx *= 0.98
        self.vy *= 0.98
        
    def draw(self, screen: pygame.Surface):
        if self.life > 0:
            alpha = int(255 * self.life)
            size = int(self.size * self.life)
            color = (*self.color, alpha)
            
            # Create a surface for the particle with per-pixel alpha
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, (size, size), size)
            
            screen.blit(particle_surface, (self.x - size, self.y - size))

class VisualEffects:
    def __init__(self, width: int, height: int, cell_size: int):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.particles: List[Particle] = []
        self.current_theme = Theme.CLASSIC
        self.color_scheme = THEMES[self.current_theme]
        self.food_pulse = 0
        self.snake_wave = 0
        
        # Initialize fonts
        try:
            pygame.font.init()
            self.title_font = pygame.font.Font(None, 60)
            self.score_font = pygame.font.Font(None, 36)
            self.menu_font = pygame.font.Font(None, 30)
        except Exception as e:
            logger.error(f"Error initializing fonts: {e}")
            self.title_font = None
            self.score_font = None
            self.menu_font = None
            
    def set_theme(self, theme: Theme):
        """Change the current color theme"""
        try:
            self.current_theme = theme
            self.color_scheme = THEMES[theme]
            logger.info(f"Theme changed to: {theme.value}")
        except Exception as e:
            logger.error(f"Error setting theme: {e}")
            
    def draw_gradient_background(self, screen: pygame.Surface):
        """Draw a gradient background"""
        try:
            start_color = self.color_scheme.background_start
            end_color = self.color_scheme.background_end
            
            for y in range(self.height):
                ratio = y / self.height
                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                
                pygame.draw.line(screen, (r, g, b), (0, y), (self.width, y))
        except Exception as e:
            logger.error(f"Error drawing gradient: {e}")
            screen.fill(self.color_scheme.background_start)
            
    def draw_grid_lines(self, screen: pygame.Surface):
        """Draw subtle grid lines"""
        try:
            grid_color = tuple(min(255, c + 20) for c in self.color_scheme.background_end)
            
            for x in range(0, self.width, self.cell_size):
                pygame.draw.line(screen, grid_color, (x, 0), (x, self.height), 1)
            for y in range(0, self.height, self.cell_size):
                pygame.draw.line(screen, grid_color, (0, y), (self.width, y), 1)
        except Exception as e:
            logger.error(f"Error drawing grid lines: {e}")
            
    def draw_snake(self, screen: pygame.Surface, positions: List[Tuple[int, int]]):
        """Draw the snake with enhanced visuals"""
        try:
            self.snake_wave += 0.1
            
            for i, position in enumerate(positions):
                # Calculate color gradient from head to tail
                gradient_ratio = i / max(len(positions) - 1, 1)
                
                # Interpolate between head and body colors
                head_color = self.color_scheme.snake_head
                body_color = self.color_scheme.snake_body
                
                r = int(head_color[0] + (body_color[0] - head_color[0]) * gradient_ratio)
                g = int(head_color[1] + (body_color[1] - head_color[1]) * gradient_ratio)
                b = int(head_color[2] + (body_color[2] - head_color[2]) * gradient_ratio)
                
                # Add wave effect
                wave_offset = math.sin(self.snake_wave + i * 0.5) * 2
                
                # Draw segment with rounded corners
                rect = pygame.Rect(
                    position[0] * self.cell_size + wave_offset,
                    position[1] * self.cell_size,
                    self.cell_size - 2,
                    self.cell_size - 2
                )
                
                # Draw segment
                pygame.draw.rect(screen, (r, g, b), rect, border_radius=5)
                
                # Draw outline
                pygame.draw.rect(screen, self.color_scheme.snake_outline, rect, 2, border_radius=5)
                
                # Draw eyes on the head
                if i == 0:
                    self._draw_snake_eyes(screen, position)
                    
        except Exception as e:
            logger.error(f"Error drawing snake: {e}")
            
    def _draw_snake_eyes(self, screen: pygame.Surface, head_position: Tuple[int, int]):
        """Draw eyes on the snake's head"""
        try:
            head_x = head_position[0] * self.cell_size + self.cell_size // 2
            head_y = head_position[1] * self.cell_size + self.cell_size // 2
            
            eye_offset = self.cell_size // 4
            eye_size = 3
            
            # Draw eyes
            pygame.draw.circle(screen, (255, 255, 255), 
                             (head_x - eye_offset, head_y), eye_size)
            pygame.draw.circle(screen, (255, 255, 255), 
                             (head_x + eye_offset, head_y), eye_size)
            
            # Draw pupils
            pygame.draw.circle(screen, (0, 0, 0), 
                             (head_x - eye_offset, head_y), eye_size // 2)
            pygame.draw.circle(screen, (0, 0, 0), 
                             (head_x + eye_offset, head_y), eye_size // 2)
        except Exception as e:
            logger.error(f"Error drawing snake eyes: {e}")
            
    def draw_food(self, screen: pygame.Surface, position: Tuple[int, int]):
        """Draw food with pulsing glow effect"""
        try:
            self.food_pulse += 0.1
            pulse_size = math.sin(self.food_pulse) * 3
            
            food_x = position[0] * self.cell_size + self.cell_size // 2
            food_y = position[1] * self.cell_size + self.cell_size // 2
            
            # Draw glow effect
            glow_radius = self.cell_size // 2 + pulse_size + 5
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            
            for i in range(glow_radius, 0, -1):
                alpha = int(50 * (1 - i / glow_radius))
                color = (*self.color_scheme.food_glow, alpha)
                pygame.draw.circle(glow_surface, color, (glow_radius, glow_radius), i)
                
            screen.blit(glow_surface, (food_x - glow_radius, food_y - glow_radius))
            
            # Draw food
            food_radius = self.cell_size // 2 - 2 + pulse_size
            pygame.draw.circle(screen, self.color_scheme.food, 
                             (food_x, food_y), int(food_radius))
            
            # Draw highlight
            highlight_offset = food_radius // 3
            pygame.draw.circle(screen, (255, 255, 255), 
                             (food_x - highlight_offset, food_y - highlight_offset), 
                             int(food_radius // 4))
        except Exception as e:
            logger.error(f"Error drawing food: {e}")
            
    def create_eat_particles(self, position: Tuple[int, int]):
        """Create particle effect when food is eaten"""
        try:
            particle_x = position[0] * self.cell_size + self.cell_size // 2
            particle_y = position[1] * self.cell_size + self.cell_size // 2
            
            for _ in range(20):
                self.particles.append(Particle(particle_x, particle_y, self.color_scheme.particle))
                
            logger.debug(f"Created {20} particles at position {position}")
        except Exception as e:
            logger.error(f"Error creating particles: {e}")
            
    def update_particles(self):
        """Update and remove dead particles"""
        try:
            self.particles = [p for p in self.particles if p.life > 0]
            for particle in self.particles:
                particle.update()
        except Exception as e:
            logger.error(f"Error updating particles: {e}")
            
    def draw_particles(self, screen: pygame.Surface):
        """Draw all active particles"""
        try:
            for particle in self.particles:
                particle.draw(screen)
        except Exception as e:
            logger.error(f"Error drawing particles: {e}")
            
    def draw_text_with_shadow(self, screen: pygame.Surface, text: str, font: pygame.font.Font, 
                             x: int, y: int, color: Optional[Tuple[int, int, int]] = None):
        """Draw text with a shadow effect"""
        try:
            if font is None:
                return
                
            if color is None:
                color = self.color_scheme.text
                
            # Draw shadow
            shadow_surface = font.render(text, True, self.color_scheme.text_shadow)
            shadow_rect = shadow_surface.get_rect(center=(x + 2, y + 2))
            screen.blit(shadow_surface, shadow_rect)
            
            # Draw text
            text_surface = font.render(text, True, color)
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
        except Exception as e:
            logger.error(f"Error drawing text with shadow: {e}")
            
    def draw_score_display(self, screen: pygame.Surface, score: int, high_score: int):
        """Draw the score display with enhanced styling"""
        try:
            # Draw score background
            score_bg = pygame.Surface((self.width, 60), pygame.SRCALPHA)
            pygame.draw.rect(score_bg, (0, 0, 0, 100), (0, 0, self.width, 60))
            screen.blit(score_bg, (0, 0))
            
            # Draw scores
            self.draw_text_with_shadow(screen, f"Score: {score}", self.score_font, 
                                     self.width // 4, 30)
            self.draw_text_with_shadow(screen, f"High Score: {high_score}", self.score_font, 
                                     3 * self.width // 4, 30)
        except Exception as e:
            logger.error(f"Error drawing score display: {e}")
            
    def draw_game_over_screen(self, screen: pygame.Surface, score: int, high_score: int):
        """Draw game over screen with enhanced visuals"""
        try:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Draw game over text
            self.draw_text_with_shadow(screen, "GAME OVER", self.title_font,
                                     self.width // 2, self.height // 2 - 100)
            
            # Draw score
            score_color = (255, 215, 0) if score == high_score else self.color_scheme.text
            self.draw_text_with_shadow(screen, f"Final Score: {score}", self.score_font,
                                     self.width // 2, self.height // 2 - 30, score_color)
            
            if score == high_score:
                self.draw_text_with_shadow(screen, "NEW HIGH SCORE!", self.score_font,
                                         self.width // 2, self.height // 2 + 10, (255, 215, 0))
            
            # Draw instructions
            self.draw_text_with_shadow(screen, "Press SPACE to play again", self.menu_font,
                                     self.width // 2, self.height // 2 + 60)
            self.draw_text_with_shadow(screen, "Press T to change theme", self.menu_font,
                                     self.width // 2, self.height // 2 + 90)
            self.draw_text_with_shadow(screen, "Press ESC to quit", self.menu_font,
                                     self.width // 2, self.height // 2 + 120)
        except Exception as e:
            logger.error(f"Error drawing game over screen: {e}")
            
    def draw_main_menu(self, screen: pygame.Surface):
        """Draw the main menu screen"""
        try:
            # Draw gradient background
            self.draw_gradient_background(screen)
            
            # Draw title
            self.draw_text_with_shadow(screen, "SNAKE GAME", self.title_font,
                                     self.width // 2, self.height // 4)
            
            # Draw menu options
            menu_items = [
                "Press SPACE to start",
                "Press T to change theme",
                "Press ESC to quit",
                "",
                f"Current Theme: {self.current_theme.value.title()}"
            ]
            
            y_offset = self.height // 2
            for item in menu_items:
                if item:
                    self.draw_text_with_shadow(screen, item, self.menu_font,
                                             self.width // 2, y_offset)
                y_offset += 40
                
        except Exception as e:
            logger.error(f"Error drawing main menu: {e}")