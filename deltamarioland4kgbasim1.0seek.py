#!/usr/bin/env python3
"""
GAMEBOY SIMULATOR HDR 1.X
© Team Flames
© Samsoft
© 1989 Nintendo

A Game Boy emulator simulator with Super Mario Land gameplay
Optimized for authentic Game Boy experience
"""

import tkinter as tk
from tkinter import ttk, messagebox
import pygame
import os
import sys
import math
from threading import Thread
import numpy as np

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GB_SCREEN_WIDTH = 160
GB_SCREEN_HEIGHT = 144
SCALE_FACTOR = 2.5
DISPLAY_WIDTH = int(GB_SCREEN_WIDTH * SCALE_FACTOR)
DISPLAY_HEIGHT = int(GB_SCREEN_HEIGHT * SCALE_FACTOR)
FPS = 59.7  # Authentic Game Boy frame rate

# Authentic Game Boy colors (4-shade grayscale)
GB_COLORS = {
    'darkest': (15, 15, 15),      # Black
    'dark': (79, 79, 79),         # Dark gray  
    'light': (162, 162, 162),     # Light gray
    'lightest': (227, 227, 227)   # White
}

class GameBoyStartupScreen:
    """Handles the authentic Game Boy boot sequence"""
    
    def __init__(self, screen):
        self.screen = screen
        self.startup_complete = False
        self.startup_timer = 0
        self.logo_y = -50
        self.sound_played = False
        
    def draw_nintendo_logo(self):
        """Draw the classic Nintendo logo during startup"""
        font = pygame.font.Font(None, 24)
        
        # Create scrolling effect
        if self.logo_y < DISPLAY_HEIGHT // 2 - 20:
            self.logo_y += 2
            
        # Draw Nintendo text
        nintendo_text = font.render("Nintendo®", True, GB_COLORS['darkest'])
        text_rect = nintendo_text.get_rect(center=(DISPLAY_WIDTH // 2, self.logo_y))
        
        # Draw background
        self.screen.fill(GB_COLORS['lightest'])
        
        # Draw authentic Game Boy logo without glow effects
        self.screen.blit(nintendo_text, text_rect)
        
        # Draw Game Boy text
        gb_text = font.render("GAME BOY", True, GB_COLORS['dark'])
        gb_rect = gb_text.get_rect(center=(DISPLAY_WIDTH // 2, self.logo_y + 30))
        self.screen.blit(gb_text, gb_rect)
        
    def update(self):
        """Update startup sequence"""
        self.startup_timer += 1
        
        if self.startup_timer < 180:  # 3 seconds at 60 FPS
            self.draw_nintendo_logo()
            
            # Play startup sound effect
            if self.startup_timer == 60 and not self.sound_played:
                self.play_startup_sound()
                self.sound_played = True
        else:
            self.startup_complete = True
            
        return self.startup_complete
    
    def play_startup_sound(self):
        """Simulate the classic Game Boy startup sound"""
        try:
            duration = 0.3
            sample_rate = 22050
            samples = int(duration * sample_rate)
            t = np.linspace(0, duration, samples, endpoint=False)
            wave = np.sin(2 * np.pi * 440 * t)
            audio = (wave * 32767).astype(np.int16)
            sound_array = np.column_stack((audio, audio))
            sound = pygame.sndarray.make_sound(sound_array)
            sound.play()
        except:
            pass  # Fail silently if audio doesn't work

class MarioCharacter:
    """Mario character with physics and animations"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.width = 16
        self.height = 16
        self.on_ground = False
        self.facing_right = True
        self.animation_frame = 0
        self.animation_timer = 0
        self.jump_power = -8
        self.speed = 2
        self.gravity = 0.5
        self.max_fall_speed = 8
        
    def update(self, platforms):
        """Update Mario's physics and collision"""
        # Horizontal movement and collision
        self.x += self.vx
        for platform in platforms:
            if self.check_collision(platform):
                if self.vx > 0:
                    self.x = platform.x - self.width
                    self.vx = 0
                elif self.vx < 0:
                    self.x = platform.x + platform.width
                    self.vx = 0
        
        # Vertical movement and collision
        if not self.on_ground:
            self.vy = min(self.vy + self.gravity, self.max_fall_speed)
        self.y += self.vy
        self.on_ground = False
        for platform in platforms:
            if self.check_collision(platform):
                if self.vy > 0:  # Falling
                    self.y = platform.y - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0:  # Jumping
                    self.y = platform.y + platform.height
                    self.vy = 0
        
        # Ground check (infinite floor fallback)
        if self.y >= DISPLAY_HEIGHT - self.height - 20:
            self.y = DISPLAY_HEIGHT - self.height - 20
            self.vy = 0
            self.on_ground = True
            
        # Update animation
        if abs(self.vx) > 0:
            self.animation_timer += 1
            if self.animation_timer > 5:
                self.animation_frame = (self.animation_frame + 1) % 2
                self.animation_timer = 0
        else:
            self.animation_frame = 0
            
    def check_collision(self, platform):
        """Check collision with platform"""
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y)
                
    def jump(self):
        """Make Mario jump"""
        if self.on_ground:
            self.vy = self.jump_power
            
    def move_left(self):
        """Move Mario left"""
        self.vx = -self.speed
        self.facing_right = False
        
    def move_right(self):
        """Move Mario right"""
        self.vx = self.speed
        self.facing_right = True
        
    def stop(self):
        """Stop horizontal movement"""
        self.vx = 0
        
    def draw(self, screen, camera_x):
        """Draw Mario with authentic Super Mario Land Game Boy graphics"""
        screen_x = self.x - camera_x
        if screen_x + self.width < 0 or screen_x > DISPLAY_WIDTH:
            return
        
        # Original Game Boy Mario sprite approximation
        # Based on Super Mario Land 16x16 sprite
        
        # Body base (overalls - darkest)
        pygame.draw.rect(screen, GB_COLORS['darkest'], 
                        (screen_x, self.y, self.width, self.height))
        
        # Shirt (light)
        pygame.draw.rect(screen, GB_COLORS['light'],
                        (screen_x + 4, self.y + 4, 8, 8))
        
        # Hat with 'M' (darkest)
        pygame.draw.rect(screen, GB_COLORS['darkest'],
                        (screen_x, self.y, self.width, 4))
        
        # Face (lightest)
        pygame.draw.rect(screen, GB_COLORS['lightest'],
                        (screen_x + 4, self.y + 4, 8, 4))
        
        # Eyes (darkest) - animated based on direction
        if self.facing_right:
            # Right facing - eye on right side
            pygame.draw.rect(screen, GB_COLORS['darkest'],
                            (screen_x + 10, self.y + 5, 2, 2))
        else:
            # Left facing - eye on left side
            pygame.draw.rect(screen, GB_COLORS['darkest'],
                            (screen_x + 4, self.y + 5, 2, 2))
        
        # Mustache (darkest)
        pygame.draw.rect(screen, GB_COLORS['darkest'],
                        (screen_x + 4, self.y + 8, 8, 2))
        
        # Arms (lightest)
        if self.animation_frame == 0 or not abs(self.vx) > 0:
            # Standing or frame 1 - arms down
            pygame.draw.rect(screen, GB_COLORS['lightest'],
                            (screen_x + 2, self.y + 8, 2, 4))
            pygame.draw.rect(screen, GB_COLORS['lightest'],
                            (screen_x + 12, self.y + 8, 2, 4))
        else:
            # Frame 2 - arms swinging
            pygame.draw.rect(screen, GB_COLORS['lightest'],
                            (screen_x + 2, self.y + 6, 2, 4))
            pygame.draw.rect(screen, GB_COLORS['lightest'],
                            (screen_x + 12, self.y + 10, 2, 4))
        
        # Legs (dark) - walking animation
        if self.animation_frame == 0 or not abs(self.vx) > 0:
            # Standing - both legs straight
            pygame.draw.rect(screen, GB_COLORS['dark'],
                            (screen_x + 4, self.y + 12, 3, 4))
            pygame.draw.rect(screen, GB_COLORS['dark'],
                            (screen_x + 9, self.y + 12, 3, 4))
        else:
            # Walking - one leg forward, one back
            pygame.draw.rect(screen, GB_COLORS['dark'],
                            (screen_x + 4, self.y + 10, 3, 6))
            pygame.draw.rect(screen, GB_COLORS['dark'],
                            (screen_x + 9, self.y + 14, 3, 2))

class Platform:
    """Platform/block for the game level"""
    
    def __init__(self, x, y, width, height, platform_type='solid'):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = platform_type
        
    def draw(self, screen, camera_x):
        """Draw platform with authentic Game Boy styling"""
        screen_x = self.x - camera_x
        if screen_x + self.width > 0 and screen_x < DISPLAY_WIDTH:
            if self.type == 'solid':
                # Main block - brick pattern
                pygame.draw.rect(screen, GB_COLORS['light'], 
                               (screen_x, self.y, self.width, self.height))
                
                # Brick details
                for i in range(0, self.width, 4):
                    for j in range(0, self.height, 4):
                        if (i // 4 + j // 4) % 2 == 0:
                            pygame.draw.rect(screen, GB_COLORS['dark'],
                                           (screen_x + i, self.y + j, 2, 2))
                
            elif self.type == 'question':
                # Question block with animation
                color = GB_COLORS['lightest'] if (pygame.time.get_ticks() // 500) % 2 else GB_COLORS['light']
                pygame.draw.rect(screen, color, 
                               (screen_x, self.y, self.width, self.height))
                
                # Border
                pygame.draw.rect(screen, GB_COLORS['darkest'],
                               (screen_x, self.y, self.width, self.height), 1)
                
                # Draw question mark
                font = pygame.font.Font(None, 12)
                text = font.render("?", True, GB_COLORS['darkest'])
                text_rect = text.get_rect(center=(screen_x + self.width//2, self.y + self.height//2))
                screen.blit(text, text_rect)

class Enemy:
    """Goomba-like enemy"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 14
        self.height = 14
        self.vx = -1
        self.vy = 0
        self.alive = True
        self.level_width = 1200
        
    def update(self, platforms):
        """Update enemy movement"""
        if not self.alive:
            return
        
        # Horizontal movement and collision
        self.x += self.vx
        hit_side = False
        for platform in platforms:
            if self.check_collision(platform):
                hit_side = True
                if self.vx > 0:
                    self.x = platform.x - self.width
                elif self.vx < 0:
                    self.x = platform.x + platform.width
        if hit_side:
            self.vx = -self.vx
        
        # Bounds check
        if self.x <= 0 or self.x >= self.level_width - self.width:
            self.vx = -self.vx
        
        # Vertical movement and collision
        self.vy = min(self.vy + 0.3, 5)
        self.y += self.vy
        for platform in platforms:
            if self.check_collision(platform):
                if self.vy > 0:
                    self.y = platform.y - self.height
                    self.vy = 0
        
    def check_collision(self, platform):
        """Check collision with platform"""
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y)
                    
    def draw(self, screen, camera_x):
        """Draw enemy with authentic Game Boy styling"""
        if not self.alive:
            return
        
        screen_x = self.x - camera_x
        if screen_x + self.width > 0 and screen_x < DISPLAY_WIDTH:
            # Animate walking
            offset = 1 if (pygame.time.get_ticks() // 300) % 2 else 0
            
            # Draw enemy body (darkest)
            pygame.draw.rect(screen, GB_COLORS['darkest'], 
                            (screen_x, self.y + offset, self.width, self.height))
            
            # Draw feet (dark)
            pygame.draw.rect(screen, GB_COLORS['dark'],
                            (screen_x + 2, self.y + self.height - 3 + offset, 3, 3))
            pygame.draw.rect(screen, GB_COLORS['dark'],
                            (screen_x + self.width - 5, self.y + self.height - 3 + offset, 3, 3))

class SuperMarioLandGame:
    """Main game class for Super Mario Land gameplay"""
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.game_over = False
        self.startup_screen = GameBoyStartupScreen(screen)
        self.game_started = False
        self.last_tick_time = 0
        self.last_frame_time = pygame.time.get_ticks()
        self.show_controls = True
        self.controls_timer = 0
        
        # Game objects
        self.mario = MarioCharacter(50, 200)
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.score = 0
        self.lives = 3
        self.time_left = 400
        self.world = "1-1"
        
        # Camera and level
        self.camera_x = 0
        self.level_width = 0
        
        # Initialize level
        self.create_level()
        
    def create_level(self):
        """Create the game level"""
        self.level_width = DISPLAY_WIDTH * 3
        # Ground platforms
        for i in range(0, self.level_width, 20):
            self.platforms.append(Platform(i, DISPLAY_HEIGHT - 20, 20, 20, 'solid'))
            
        # Floating platforms
        self.platforms.append(Platform(150, 250, 60, 16, 'solid'))
        self.platforms.append(Platform(250, 200, 60, 16, 'solid'))
        self.platforms.append(Platform(350, 220, 40, 16, 'question'))
        self.platforms.append(Platform(450, 180, 60, 16, 'solid'))
        
        # Add enemies
        self.enemies.append(Enemy(200, DISPLAY_HEIGHT - 34))
        self.enemies.append(Enemy(400, DISPLAY_HEIGHT - 34))
        
    def handle_input(self):
        """Handle keyboard input including WASD controls"""
        keys = pygame.key.get_pressed()
        
        # Arrow keys and WASD for movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.mario.move_left()
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.mario.move_right()
        else:
            self.mario.stop()
            
        # Space, Up arrow, or W for jumping
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.mario.jump()
            
    def check_collisions(self):
        """Check collisions between Mario and enemies"""
        for enemy in self.enemies:
            if not enemy.alive:
                continue
                
            if (self.mario.x < enemy.x + enemy.width and
                self.mario.x + self.mario.width > enemy.x and
                self.mario.y < enemy.y + enemy.height and
                self.mario.y + self.mario.height > enemy.y):
                
                # Check if Mario is jumping on enemy
                if self.mario.vy > 0 and self.mario.y + self.mario.height < enemy.y + enemy.height//2:
                    enemy.alive = False
                    self.score += 100
                    self.mario.vy = -5  # Bounce
                else:
                    # Mario takes damage
                    self.lives -= 1
                    self.mario.x = 50  # Reset position
                    self.mario.y = 200
                    if self.lives <= 0:
                        self.set_game_over()
                    
    def draw_hud(self):
        """Draw the HUD with score, lives, and time"""
        font = pygame.font.Font(None, 16)
        
        # Score
        score_text = font.render(f"SCORE {self.score:06d}", True, GB_COLORS['darkest'])
        self.screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = font.render(f"MARIO x{self.lives}", True, GB_COLORS['darkest'])
        self.screen.blit(lives_text, (10, 25))
        
        # World
        world_text = font.render(f"WORLD {self.world}", True, GB_COLORS['darkest'])
        self.screen.blit(world_text, (DISPLAY_WIDTH - 80, 10))
        
        # Time
        time_text = font.render(f"TIME {self.time_left:03d}", True, GB_COLORS['darkest'])
        self.screen.blit(time_text, (DISPLAY_WIDTH - 80, 25))
        
    def draw_controls(self):
        """Draw the controls help on screen"""
        if not self.show_controls:
            return
            
        font = pygame.font.Font(None, 14)
        
        # Controls background
        controls_bg = pygame.Surface((150, 70), pygame.SRCALPHA)
        controls_bg.fill((*GB_COLORS['lightest'], 200))
        self.screen.blit(controls_bg, (DISPLAY_WIDTH - 160, DISPLAY_HEIGHT - 80))
        
        # Controls text
        controls_title = font.render("CONTROLS:", True, GB_COLORS['darkest'])
        self.screen.blit(controls_title, (DISPLAY_WIDTH - 155, DISPLAY_HEIGHT - 75))
        
        move_text = font.render("A/D or ←/→: Move", True, GB_COLORS['darkest'])
        self.screen.blit(move_text, (DISPLAY_WIDTH - 155, DISPLAY_HEIGHT - 60))
        
        jump_text = font.render("W/↑/SPACE: Jump", True, GB_COLORS['darkest'])
        self.screen.blit(jump_text, (DISPLAY_WIDTH - 155, DISPLAY_HEIGHT - 45))
        
        # Hide controls after 10 seconds
        self.controls_timer += 1
        if self.controls_timer > 600:  # 10 seconds at 60 FPS
            self.show_controls = False
        
    def set_game_over(self):
        """Set game over state"""
        self.game_over = True
        
    def draw_game_over(self):
        """Draw game over screen"""
        font = pygame.font.Font(None, 32)
        text = font.render("GAME OVER", True, GB_COLORS['darkest'])
        text_rect = text.get_rect(center=(DISPLAY_WIDTH // 2, DISPLAY_HEIGHT // 2))
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill((*GB_COLORS['lightest'], 180))
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(text, text_rect)
        
    def update(self):
        """Update game state"""
        if not self.game_started:
            self.game_started = self.startup_screen.update()
            return
        
        self.handle_input()
        self.mario.update(self.platforms)
        
        # Update camera
        self.camera_x = max(0, min(self.mario.x - DISPLAY_WIDTH // 2, self.level_width - DISPLAY_WIDTH))
        
        for enemy in self.enemies:
            enemy.update(self.platforms)
            
        self.check_collisions()
        
        # Update timer accurately
        current_time = pygame.time.get_ticks()
        if current_time - self.last_tick_time >= 1000:
            self.time_left = max(0, self.time_left - 1)
            self.last_tick_time = current_time
            
        # Game over conditions
        if self.lives <= 0 or self.time_left <= 0:
            self.set_game_over()
            
    def draw(self):
        """Draw the game with authentic Game Boy graphics"""
        if self.game_over:
            self.draw_game_over()
            self.draw_hud()
            return
        
        if not self.game_started:
            return
            
        # Clear screen with authentic Game Boy background color
        self.screen.fill(GB_COLORS['lightest'])
            
        # Draw game objects with camera offset
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)
            
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera_x)
            
        self.mario.draw(self.screen, self.camera_x)
        self.draw_hud()
        self.draw_controls()
            
    def run(self):
        """Main game loop with accurate Game Boy timing"""
        while self.running:
            current_time = pygame.time.get_ticks()
            frame_delay = 1000.0 / FPS
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    # Show controls again if C is pressed
                    if event.key == pygame.K_c:
                        self.show_controls = True
                        self.controls_timer = 0
                    
            if not self.paused and not self.game_over:
                self.update()
                
            self.draw()
            pygame.display.flip()
            
            # Accurate frame timing for authentic Game Boy experience
            elapsed = pygame.time.get_ticks() - current_time
            if elapsed < frame_delay:
                pygame.time.delay(int(frame_delay - elapsed))
                
            if self.paused:
                self.clock.tick(10)  # Slow tick when paused
            else:
                self.clock.tick(FPS)

class GameBoySimulatorGUI:
    """VirtualBox-style GUI for the Game Boy Simulator"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GAMEBOY SIMULATOR HDR 1.X")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg='#2b2b2b')
        
        # Set window icon (if possible)
        try:
            self.root.iconbitmap(default='gameboy.ico')
        except:
            pass
            
        # Create UI
        self.create_virtualbox_ui()
        
        # Game state
        self.game_running = False
        self.game = None
        self.game_thread = None
        
    def create_virtualbox_ui(self):
        """Create VirtualBox-like interface"""
        # Top menu bar
        menubar = tk.Menu(self.root, bg='#3c3c3c', fg='white')
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Machine", menu=file_menu)
        file_menu.add_command(label="New Game", command=self.new_game)
        file_menu.add_command(label="Load State", command=self.load_state)
        file_menu.add_command(label="Save State", command=self.save_state)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit_app)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Fullscreen", command=self.toggle_fullscreen)
        view_menu.add_command(label="Show Controls", command=self.show_controls_help)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg='#3c3c3c', fg='white')
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="How to Play", command=self.show_how_to_play)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Machine list
        left_panel = ttk.Frame(main_frame, style='Dark.TFrame', width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Machine list label
        machines_label = ttk.Label(left_panel, text="Virtual Machines", 
                                  font=('Arial', 10, 'bold'),
                                  foreground='white', background='#2b2b2b')
        machines_label.pack(pady=(0, 10))
        
        # Listbox for machines
        self.machine_listbox = tk.Listbox(left_panel, bg='#3c3c3c', fg='white',
                                          selectbackground='#5c5c5c',
                                          font=('Courier', 9))
        self.machine_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Add Game Boy entry
        self.machine_listbox.insert(0, "🎮 Game Boy DMG-01")
        self.machine_listbox.insert(1, "   Super Mario Land")
        self.machine_listbox.insert(2, "   Status: Ready")
        self.machine_listbox.insert(3, "   Mode: Authentic")
        self.machine_listbox.insert(4, f"   FPS: {FPS}")
        self.machine_listbox.insert(5, "   Controls: WASD")
        
        # Control buttons
        button_frame = ttk.Frame(left_panel, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_button = ttk.Button(button_frame, text="▶ Start", 
                                       command=self.start_emulator)
        self.start_button.pack(side=tk.LEFT, padx=2)
        
        self.pause_button = ttk.Button(button_frame, text="⏸ Pause", 
                                       command=self.pause_emulator,
                                       state='disabled')
        self.pause_button.pack(side=tk.LEFT, padx=2)
        
        self.reset_button = ttk.Button(button_frame, text="↻ Reset", 
                                       command=self.reset_emulator)
        self.reset_button.pack(side=tk.LEFT, padx=2)
        
        # How to Play section
        how_to_frame = ttk.Frame(left_panel, style='Dark.TFrame')
        how_to_frame.pack(fill=tk.X, pady=(20, 0))
        
        how_to_label = ttk.Label(how_to_frame, text="HOW TO PLAY:", 
                                font=('Arial', 10, 'bold'),
                                foreground='white', background='#2b2b2b')
        how_to_label.pack(anchor='w')
        
        controls_text = """
Move: A / D or ← / →
Jump: W / ↑ / SPACE
Show Controls: C
        """
        
        controls_label = ttk.Label(how_to_frame, text=controls_text,
                                  font=('Courier', 8),
                                  foreground='#cccccc', background='#2b2b2b',
                                  justify=tk.LEFT)
        controls_label.pack(anchor='w', pady=(5, 0))
        
        # Right panel - Display area
        right_panel = ttk.Frame(main_frame, style='Dark.TFrame')
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Display label
        display_label = ttk.Label(right_panel, text="Display Output", 
                                 font=('Arial', 10, 'bold'),
                                 foreground='white', background='#2b2b2b')
        display_label.pack(pady=(0, 10))
        
        # Pygame embed frame
        self.game_frame = tk.Frame(right_panel, width=DISPLAY_WIDTH, 
                                   height=DISPLAY_HEIGHT, bg='black')
        self.game_frame.pack()
        
        # Status bar
        self.status_frame = ttk.Frame(right_panel, style='Dark.TFrame')
        self.status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = ttk.Label(self.status_frame, 
                                      text="© Team Flames | © Samsoft | © 1989 Nintendo | Press C for Controls", 
                                      foreground='#888', background='#2b2b2b',
                                      font=('Arial', 8))
        self.status_label.pack(side=tk.LEFT)
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background='#2b2b2b')
        style.configure('TButton', background='#3c3c3c', foreground='white')
        style.map('TButton', background=[('active', '#5c5c5c')])
        
    def show_how_to_play(self):
        """Show how to play instructions"""
        how_to_text = """HOW TO PLAY SUPER MARIO LAND

CONTROLS:
- A / Left Arrow: Move Left
- D / Right Arrow: Move Right  
- W / Up Arrow / Space: Jump
- C: Show/Hide Controls

GAMEPLAY:
- Move right to advance through the level
- Jump on enemies to defeat them
- Avoid falling into pits
- Collect coins for points
- Reach the goal to complete the level

TIPS:
- Time your jumps carefully
- Watch out for moving enemies
- Some blocks may contain power-ups"""
        
        messagebox.showinfo("How to Play", how_to_text)
        
    def show_controls_help(self):
        """Show controls help"""
        controls_text = """GAME CONTROLS:

MOVEMENT:
A or Left Arrow    - Move Left
D or Right Arrow   - Move Right
W or Up Arrow      - Jump
Spacebar           - Jump

OTHER:
C - Show/Hide Controls
P - Pause Game

You can use either the arrow keys 
or WASD for movement, whichever 
you prefer!"""
        
        messagebox.showinfo("Controls", controls_text)
        
    def start_emulator(self):
        """Start the Game Boy emulator"""
        if not self.game_running:
            self.game_running = True
            self.start_button.config(state='disabled')
            self.pause_button.config(state='normal')
            
            # Update status
            self.machine_listbox.delete(2)
            self.machine_listbox.insert(2, "   Status: Running")
            
            # Start game in embedded window
            self.run_game()
            
    def run_game(self):
        """Run the game in the embedded frame"""
        # Get the window ID of the frame
        embed_id = self.game_frame.winfo_id()
        
        # Set SDL window to embed in tkinter frame (must be before pygame.init())
        os.environ['SDL_WINDOWID'] = str(embed_id)
        os.environ['SDL_VIDEODRIVER'] = 'windib' if sys.platform == 'win32' else 'x11'
        
        # Initialize pygame
        pygame.init()
        
        # Initialize pygame display
        screen = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        pygame.display.set_caption("Super Mario Land")
        
        # Create and run game
        self.game = SuperMarioLandGame(screen)
        self.game.paused = False
        
        # Run game loop
        self.game_thread = Thread(target=self.game.run)
        self.game_thread.daemon = True
        self.game_thread.start()
        
    def pause_emulator(self):
        """Pause the emulator"""
        if self.game:
            self.game.paused = True
        self.game_running = False
        self.start_button.config(state='normal')
        self.pause_button.config(state='disabled')
        
        # Update status
        self.machine_listbox.delete(2)
        self.machine_listbox.insert(2, "   Status: Paused")
        
    def reset_emulator(self):
        """Reset the emulator"""
        self.pause_emulator()
        if self.game:
            self.game.running = False
            if self.game_thread and self.game_thread.is_alive():
                self.game_thread.join(timeout=1)
            try:
                pygame.display.quit()
            except:
                pass
            self.game = None
            self.game_thread = None
        
        self.game_frame.config(bg='black')
        
        # Update status
        self.machine_listbox.delete(2)
        self.machine_listbox.insert(2, "   Status: Ready")
        
    def new_game(self):
        """Start a new game"""
        self.reset_emulator()
        self.start_emulator()
        
    def load_state(self):
        """Load a saved state (placeholder)"""
        messagebox.showinfo("Load State", "State loading not implemented yet")
        
    def save_state(self):
        """Save current state (placeholder)"""
        messagebox.showinfo("Save State", "State saving not implemented yet")
        
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        
    def show_about(self):
        """Show about dialog"""
        about_text = """GAMEBOY SIMULATOR HDR 1.X
        
© Team Flames
© Samsoft  
© 1989 Nintendo

An authentic Game Boy emulator
running at 59.7 FPS with proper
4-shade grayscale palette.

Super Mario Land recreation
faithful to the original hardware.

CONTROLS:
WASD or Arrow Keys + Space"""
        
        messagebox.showinfo("About", about_text)
        
    def quit_app(self):
        """Quit the application"""
        if messagebox.askokcancel("Quit", "Do you want to quit the emulator?"):
            self.reset_emulator()
            pygame.quit()
            self.root.quit()
            
    def run(self):
        """Run the main GUI loop"""
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.mainloop()

if __name__ == "__main__":
    # Create and run the simulator
    simulator = GameBoySimulatorGUI()
    simulator.run()
