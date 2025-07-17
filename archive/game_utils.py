import pygame
import random
import json
import os
import logging
from datetime import datetime
from typing import List, Tuple, Dict, Optional
import math

# Initialize logging for game utilities
logger = logging.getLogger('snake_game.utils')

# Color constants
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'PURPLE': (128, 0, 128),
    'CYAN': (0, 255, 255),
    'ORANGE': (255, 165, 0),
    'PINK': (255, 192, 203),
    'DARK_GREEN': (0, 128, 0),
    'DARK_BLUE': (0, 0, 128),
    'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (192, 192, 192),
    'DARK_GRAY': (64, 64, 64)
}

# Game themes
THEMES = {
    'classic': {
        'background': COLORS['BLACK'],
        'snake': COLORS['GREEN'],
        'food': COLORS['RED'],
        'text': COLORS['WHITE'],
        'grid': None
    },
    'neon': {
        'background': COLORS['DARK_BLUE'],
        'snake': COLORS['CYAN'],
        'food': COLORS['PINK'],
        'text': COLORS['YELLOW'],
        'grid': COLORS['DARK_GRAY']
    },
    'nature': {
        'background': (34, 139, 34),
        'snake': (139, 69, 19),
        'food': (255, 69, 0),
        'text': COLORS['WHITE'],
        'grid': (46, 125, 50)
    },
    'ocean': {
        'background': (0, 119, 190),
        'snake': (255, 160, 122),
        'food': (255, 215, 0),
        'text': COLORS['WHITE'],
        'grid': (0, 150, 200)
    }
}

class Particle:
    """Particle for visual effects"""
    def __init__(self, x: float, y: float, dx: float, dy: float, color: Tuple[int, int, int], 
                 lifetime: int = 30, size: int = 3):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        
    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.lifetime -= 1
        self.dy += 0.2  # Gravity effect
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            size = int(self.size * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
    
    def is_alive(self) -> bool:
        return self.lifetime > 0

class ParticleSystem:
    """Manages particle effects"""
    def __init__(self):
        self.particles: List[Particle] = []
        
    def add_explosion(self, x: int, y: int, color: Tuple[int, int, int], count: int = 20):
        """Create an explosion effect"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            lifetime = random.randint(20, 40)
            size = random.randint(2, 5)
            self.particles.append(Particle(x, y, dx, dy, color, lifetime, size))
    
    def add_trail(self, x: int, y: int, color: Tuple[int, int, int]):
        """Create a trail effect"""
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        self.particles.append(Particle(x, y, dx, dy, color, 15, 2))
    
    def update(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
    
    def draw(self, screen):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(screen)

class PowerUp:
    """Power-up item in the game"""
    def __init__(self, position: Tuple[int, int], power_type: str):
        self.position = position
        self.type = power_type
        self.duration = 300  # frames
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 10000  # 10 seconds before disappearing
        
    def is_expired(self) -> bool:
        return pygame.time.get_ticks() - self.spawn_time > self.lifetime
    
    def get_color(self) -> Tuple[int, int, int]:
        colors = {
            'speed': COLORS['BLUE'],
            'slow': COLORS['PURPLE'],
            'invincible': COLORS['YELLOW'],
            'double_points': COLORS['ORANGE'],
            'shrink': COLORS['CYAN']
        }
        return colors.get(self.type, COLORS['WHITE'])
    
    def get_symbol(self) -> str:
        symbols = {
            'speed': 'S',
            'slow': 'L',
            'invincible': 'I',
            'double_points': '2',
            'shrink': '-'
        }
        return symbols.get(self.type, '?')

class Button:
    """UI Button component"""
    def __init__(self, x: int, y: int, width: int, height: int, text: str, 
                 color: Tuple[int, int, int] = COLORS['WHITE'],
                 bg_color: Tuple[int, int, int] = COLORS['DARK_GRAY'],
                 hover_color: Tuple[int, int, int] = COLORS['GRAY']):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.current_color = bg_color
        self.font = pygame.font.Font(None, 36)
        
    def update(self, mouse_pos: Tuple[int, int]):
        """Update button state based on mouse position"""
        if self.rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.bg_color
    
    def draw(self, screen):
        """Draw the button"""
        try:
            pygame.draw.rect(screen, self.current_color, self.rect)
            pygame.draw.rect(screen, self.color, self.rect, 3)
            
            text_surface = self.font.render(self.text, True, self.color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)
        except pygame.error as e:
            logger.error(f"Error drawing button '{self.text}': {e}")
            # Draw a simple colored rectangle as fallback
            pygame.draw.rect(screen, self.current_color, self.rect)
        except Exception as e:
            logger.error(f"Unexpected error drawing button '{self.text}': {e}")
    
    def is_clicked(self, mouse_pos: Tuple[int, int], mouse_click: bool) -> bool:
        """Check if button is clicked"""
        return mouse_click and self.rect.collidepoint(mouse_pos)

class SettingsManager:
    """Manages game settings"""
    def __init__(self, settings_file: str = "snake_settings.json"):
        self.settings_file = settings_file
        self.default_settings = {
            'sound_enabled': True,
            'music_volume': 0.7,
            'sfx_volume': 0.8,
            'difficulty': 'normal',
            'theme': 'classic',
            'show_grid': False,
            'particle_effects': True,
            'snake_speed': 10,
            'controls': {
                'up': pygame.K_UP,
                'down': pygame.K_DOWN,
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'pause': pygame.K_SPACE
            }
        }
        self.settings = self.load_settings()
    
    def load_settings(self) -> Dict:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    logger.info("Settings loaded successfully")
                    return settings
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Could not save settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value"""
        self.settings[key] = value
        self.save_settings()

class LeaderboardManager:
    """Manages game leaderboard"""
    def __init__(self, leaderboard_file: str = "snake_leaderboard.json"):
        self.leaderboard_file = leaderboard_file
        self.max_entries = 10
        self.leaderboard = self.load_leaderboard()
    
    def load_leaderboard(self) -> List[Dict]:
        """Load leaderboard from file"""
        try:
            if os.path.exists(self.leaderboard_file):
                with open(self.leaderboard_file, 'r') as f:
                    data = json.load(f)
                    logger.info("Leaderboard loaded successfully")
                    return data
        except Exception as e:
            logger.warning(f"Could not load leaderboard: {e}")
        
        return []
    
    def save_leaderboard(self):
        """Save leaderboard to file"""
        try:
            with open(self.leaderboard_file, 'w') as f:
                json.dump(self.leaderboard, f, indent=4)
            logger.info("Leaderboard saved successfully")
        except Exception as e:
            logger.error(f"Could not save leaderboard: {e}")
    
    def add_score(self, name: str, score: int, difficulty: str) -> int:
        """Add a score to the leaderboard. Returns position (0-based) or -1 if not in top 10"""
        entry = {
            'name': name[:20],  # Limit name length
            'score': score,
            'difficulty': difficulty,
            'date': datetime.now().isoformat()
        }
        
        self.leaderboard.append(entry)
        self.leaderboard.sort(key=lambda x: x['score'], reverse=True)
        self.leaderboard = self.leaderboard[:self.max_entries]
        
        position = -1
        for i, item in enumerate(self.leaderboard):
            if item == entry:
                position = i
                break
        
        self.save_leaderboard()
        return position
    
    def get_top_scores(self, count: int = 10) -> List[Dict]:
        """Get top scores"""
        return self.leaderboard[:count]
    
    def is_high_score(self, score: int) -> bool:
        """Check if score qualifies for leaderboard"""
        if len(self.leaderboard) < self.max_entries:
            return True
        return score > self.leaderboard[-1]['score']

class SoundManager:
    """Manages game sounds and music"""
    def __init__(self, settings_manager: SettingsManager):
        self.settings = settings_manager
        self.sounds = {}
        self.music_loaded = False
        
        try:
            pygame.mixer.init()
            logger.info("Sound system initialized")
        except Exception as e:
            logger.error(f"Could not initialize sound system: {e}")
    
    def load_sound(self, name: str, file_path: str):
        """Load a sound effect"""
        if not os.path.exists(file_path):
            logger.warning(f"Sound file not found: {file_path}")
            return
            
        try:
            self.sounds[name] = pygame.mixer.Sound(file_path)
            self.sounds[name].set_volume(self.settings.get('sfx_volume', 0.8))
        except Exception as e:
            logger.error(f"Could not load sound {name}: {e}")
    
    def play_sound(self, name: str):
        """Play a sound effect"""
        if not self.settings.get('sound_enabled', True):
            return
            
        if name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                logger.error(f"Could not play sound {name}: {e}")
    
    def load_music(self, file_path: str):
        """Load background music"""
        if not os.path.exists(file_path):
            logger.warning(f"Music file not found: {file_path}")
            return
            
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.settings.get('music_volume', 0.7))
            self.music_loaded = True
        except Exception as e:
            logger.error(f"Could not load music: {e}")
    
    def play_music(self, loops: int = -1):
        """Play background music"""
        if not self.settings.get('sound_enabled', True) or not self.music_loaded:
            return
            
        try:
            pygame.mixer.music.play(loops)
        except Exception as e:
            logger.error(f"Could not play music: {e}")
    
    def stop_music(self):
        """Stop background music"""
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            logger.error(f"Could not stop music: {e}")
    
    def update_volume(self):
        """Update volume levels from settings"""
        music_volume = self.settings.get('music_volume', 0.7)
        sfx_volume = self.settings.get('sfx_volume', 0.8)
        
        try:
            pygame.mixer.music.set_volume(music_volume)
            for sound in self.sounds.values():
                sound.set_volume(sfx_volume)
        except Exception as e:
            logger.error(f"Could not update volume: {e}")

class UIRenderer:
    """Handles UI rendering with better fonts and styling"""
    def __init__(self):
        self.fonts = {
            'title': pygame.font.Font(None, 72),
            'subtitle': pygame.font.Font(None, 48),
            'normal': pygame.font.Font(None, 36),
            'small': pygame.font.Font(None, 24)
        }
    
    def draw_text(self, screen, text: str, pos: Tuple[int, int], 
                  font_size: str = 'normal', color: Tuple[int, int, int] = COLORS['WHITE'],
                  center: bool = True, shadow: bool = True):
        """Draw text with optional shadow"""
        font = self.fonts.get(font_size, self.fonts['normal'])
        
        # Draw shadow
        if shadow:
            shadow_surface = font.render(text, True, COLORS['BLACK'])
            shadow_rect = shadow_surface.get_rect()
            if center:
                shadow_rect.center = (pos[0] + 2, pos[1] + 2)
            else:
                shadow_rect.topleft = (pos[0] + 2, pos[1] + 2)
            screen.blit(shadow_surface, shadow_rect)
        
        # Draw main text
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = pos
        else:
            text_rect.topleft = pos
        screen.blit(text_surface, text_rect)
    
    def draw_panel(self, screen, rect: pygame.Rect, 
                   bg_color: Tuple[int, int, int] = COLORS['DARK_GRAY'],
                   border_color: Tuple[int, int, int] = COLORS['WHITE'],
                   border_width: int = 3, alpha: int = 200):
        """Draw a semi-transparent panel"""
        panel_surface = pygame.Surface((rect.width, rect.height))
        panel_surface.set_alpha(alpha)
        panel_surface.fill(bg_color)
        screen.blit(panel_surface, rect)
        
        if border_width > 0:
            pygame.draw.rect(screen, border_color, rect, border_width)

def get_difficulty_settings(difficulty: str) -> Dict:
    """Get game settings based on difficulty"""
    settings = {
        'easy': {
            'snake_speed': 8,
            'powerup_spawn_rate': 0.02,
            'powerup_duration': 400,
            'score_multiplier': 0.8,
            'grid_size': 25
        },
        'normal': {
            'snake_speed': 10,
            'powerup_spawn_rate': 0.015,
            'powerup_duration': 300,
            'score_multiplier': 1.0,
            'grid_size': 30
        },
        'hard': {
            'snake_speed': 15,
            'powerup_spawn_rate': 0.01,
            'powerup_duration': 200,
            'score_multiplier': 1.5,
            'grid_size': 40
        },
        'extreme': {
            'snake_speed': 20,
            'powerup_spawn_rate': 0.005,
            'powerup_duration': 150,
            'score_multiplier': 2.0,
            'grid_size': 50
        }
    }
    return settings.get(difficulty, settings['normal'])

def create_gradient_background(screen, color1: Tuple[int, int, int], 
                             color2: Tuple[int, int, int], vertical: bool = True):
    """Create a gradient background"""
    width, height = screen.get_size()
    
    for i in range(height if vertical else width):
        ratio = i / (height if vertical else width)
        color = [
            int(color1[j] * (1 - ratio) + color2[j] * ratio)
            for j in range(3)
        ]
        
        if vertical:
            pygame.draw.line(screen, color, (0, i), (width, i))
        else:
            pygame.draw.line(screen, color, (i, 0), (i, height))

def draw_grid(screen, cell_size: int, color: Tuple[int, int, int] = COLORS['DARK_GRAY']):
    """Draw a grid overlay"""
    width, height = screen.get_size()
    
    for x in range(0, width, cell_size):
        pygame.draw.line(screen, color, (x, 0), (x, height), 1)
    
    for y in range(0, height, cell_size):
        pygame.draw.line(screen, color, (0, y), (width, y), 1)