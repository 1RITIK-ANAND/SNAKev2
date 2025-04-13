# Import necessary libraries
import pygame
import random
import sys # Used for sys.exit()

# Initialize Pygame
pygame.init()

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20  # Size of each grid cell (and snake segment/food)

# Calculate grid dimensions based on screen size and grid size
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Game speed - Frames Per Second (initial)
INITIAL_FPS = 10
FPS_INCREASE_RATE = 5 # Increase FPS every N points

# Colors (RGB tuples)
COLOR_BACKGROUND = (20, 20, 20)     # Dark grey background
COLOR_GRID = (40, 40, 40)         # Slightly lighter grid lines
COLOR_TEXT = (255, 255, 255)    # White text
COLOR_FOOD = (255, 0, 0)        # Red food
COLOR_GAME_OVER = (200, 0, 0)   # Reddish for Game Over text

# List of colors for the snake to cycle through
SNAKE_COLORS = [
    (0, 255, 0),       # Green
    (0, 200, 255),     # Light Blue
    (255, 255, 0),     # Yellow
    (255, 0, 255),     # Magenta
    (0, 255, 255),     # Cyan
    (255, 165, 0),     # Orange
    (138, 43, 226),    # Blue Violet
    (255, 105, 180),   # Hot Pink
]

# Directions mapping (vector change in x, y grid coordinates)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# --- Classes ---

class Snake:
    """Represents the snake player."""
    def __init__(self):
        """Initializes the snake's properties."""
        self.reset() # Initialize state via reset method

    def get_head_position(self):
        """Returns the grid coordinates of the snake's head."""
        return self.positions[0]

    def update(self):
        """
        Updates the snake's position based on its direction.
        Checks for collisions (self and wall).
        Returns True if game over, False otherwise.
        """
        # Update direction only if a valid turn is buffered
        # Prevent immediate 180-degree turns
        if self.next_direction and \
           (self.next_direction[0] * -1, self.next_direction[1] * -1) != self.direction:
            self.direction = self.next_direction
            self.next_direction = None # Clear buffered direction

        # Calculate new head position based on current direction
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        new_head_pos = (head_x + dir_x, head_y + dir_y)

        # --- Collision Checks ---
        # 1. Wall Collision Check
        if not (0 <= new_head_pos[0] < GRID_WIDTH and 0 <= new_head_pos[1] < GRID_HEIGHT):
            return True # Game Over - Hit wall

        # 2. Self Collision Check
        # Check if the new head position collides with any existing body segment
        if new_head_pos in self.positions:
             # Allow collision only if it's the tail position and snake isn't growing
             # (handles the case where the snake moves into the spot its tail just left)
             if new_head_pos == self.positions[-1] and self.grow_pending == 0:
                 pass # Technically not a collision if tail is about to move
             else:
                 return True # Game Over - Hit self

        # --- Move Snake ---
        # Insert new head position at the beginning of the list
        self.positions.insert(0, new_head_pos)

        # Handle snake growth
        if self.grow_pending > 0:
            self.grow_pending -= 1
        else:
            # If not growing, remove the tail segment
            self.positions.pop()

        return False # Game Continues

    def grow(self):
        """Increases score, marks snake for growth, and checks for color change."""
        self.grow_pending += 1
        self.score += 1

        # Change snake color every 10 points (and not at score 0)
        if self.score > 0 and self.score % 10 == 0:
            self.color_index = (self.color_index + 1) % len(SNAKE_COLORS)

    def change_direction(self, new_direction):
        """Buffers the next direction change."""
        # Buffer the direction change to be applied in the next update()
        self.next_direction = new_direction

    def get_color(self):
        """Returns the current color of the snake."""
        return SNAKE_COLORS[self.color_index]

    def reset(self):
        """Resets the snake to its initial state."""
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)] # Start in center
        self.direction = random.choice([UP, DOWN, LEFT, RIGHT]) # Start in random direction
        self.next_direction = self.direction # No buffered direction initially
        self.score = 0
        self.color_index = 0 # Start with the first color
        self.grow_pending = 0 # How many segments to add in upcoming updates

class Food:
    """Represents the food item."""
    def __init__(self):
        """Initializes food position."""
        self.position = (0, 0) # Dummy position, will be randomized
        self.randomize_position([]) # Initial randomization

    def randomize_position(self, snake_positions):
        """
        Sets the food to a random position on the grid, avoiding snake body.
        """
        while True:
            self.position = (random.randint(0, GRID_WIDTH - 1),
                             random.randint(0, GRID_HEIGHT - 1))
            # Ensure food doesn't spawn on top of the snake
            if self.position not in snake_positions:
                break

    def get_position(self):
        """Returns the grid coordinates of the food."""
        return self.position

# --- Drawing Functions ---

def draw_grid(surface):
    """Draws the background grid lines."""
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (0, y), (SCREEN_WIDTH, y))
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT))

def draw_snake(surface, snake):
    """Draws the snake segments."""
    snake_color = snake.get_color()
    for i, pos in enumerate(snake.positions):
        rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        # Slightly different color for head (optional visual distinction)
        segment_color = tuple(max(0, c-20) for c in snake_color) if i > 0 else snake_color
        pygame.draw.rect(surface, segment_color, rect)
        # Optional: Add border to segments
        # pygame.draw.rect(surface, COLOR_GRID, rect, 1)

def draw_food(surface, food):
    """Draws the food item."""
    rect = pygame.Rect(food.get_position()[0] * GRID_SIZE,
                       food.get_position()[1] * GRID_SIZE,
                       GRID_SIZE, GRID_SIZE)
    pygame.draw.rect(surface, COLOR_FOOD, rect)
    # Optional: Add border to food
    # pygame.draw.rect(surface, COLOR_BACKGROUND, rect, 1)

def draw_score(surface, score):
    """Draws the current score on the screen."""
    font = pygame.font.SysFont('arial', 24, bold=True) # Use system font Arial
    text_surface = font.render(f'Score: {score}', True, COLOR_TEXT)
    # Position score at top-left
    surface.blit(text_surface, (10, 10))

def draw_game_over_screen(surface, score):
    """Displays the Game Over message and instructions."""
    surface.fill(COLOR_BACKGROUND) # Clear screen with background color

    # Fonts
    font_large = pygame.font.SysFont('arial', 60, bold=True)
    font_small = pygame.font.SysFont('arial', 30)

    # Create text surfaces
    game_over_text = font_large.render('Game Over', True, COLOR_GAME_OVER)
    score_text = font_small.render(f'Final Score: {score}', True, COLOR_TEXT)
    restart_text = font_small.render('Press R to Restart or Q to Quit', True, COLOR_TEXT)

    # Calculate positions (centered)
    go_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

    # Draw text surfaces onto the main screen surface
    surface.blit(game_over_text, go_rect)
    surface.blit(score_text, score_rect)
    surface.blit(restart_text, restart_rect)

# --- Main Game Function ---

def main():
    """Main function to run the Snake game."""
    # Set up display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Python Snake Game')
    clock = pygame.time.Clock() # Clock object to control frame rate

    # Create game objects
    snake = Snake()
    food = Food()
    food.randomize_position(snake.positions) # Initial food placement

    game_over = False # Game state flag

    # Main game loop
    running = True
    while running:
        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False # Exit loop if window is closed
            elif event.type == pygame.KEYDOWN:
                if game_over: # Handle input only on game over screen
                    if event.key == pygame.K_r: # Restart
                        # Reset game state
                        snake.reset()
                        food.randomize_position(snake.positions)
                        game_over = False
                    elif event.key == pygame.K_q: # Quit
                        running = False
                else: # Handle input during active gameplay
                    if event.key == pygame.K_UP:
                        snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction(RIGHT)

        # --- Game Logic (only if game is not over) ---
        if not game_over:
            # Update snake position and check for collisions
            game_over = snake.update()

            # Check if snake ate the food
            if not game_over and snake.get_head_position() == food.get_position():
                snake.grow() # Increase score, flag growth, check color change
                food.randomize_position(snake.positions) # New food location

        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND) # Clear screen each frame

        if game_over:
            draw_game_over_screen(screen, snake.score)
        else:
            # Draw game elements during active play
            draw_grid(screen) # Draw grid lines
            draw_snake(screen, snake)
            draw_food(screen, food)
            draw_score(screen, snake.score)

        # Update the full display surface
        pygame.display.flip() # Or pygame.display.update()

        # --- Frame Rate Control ---
        # Calculate current FPS based on score
        current_fps = INITIAL_FPS + (snake.score // FPS_INCREASE_RATE)
        clock.tick(current_fps) # Limit frame rate

    # --- Game Exit ---
    pygame.quit()
    sys.exit()

# Entry point: Run the main function when the script is executed
if __name__ == "__main__":
    main()
    