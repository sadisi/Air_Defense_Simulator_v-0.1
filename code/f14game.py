import pygame
import random

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1200, 1000
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Air Defense Simulation Game")

# Load and resize assets
background = pygame.image.load("assets/images/skybg.jpg")
background = pygame.transform.scale(background, (width, height))
missile_image = pygame.image.load("assets/images/missiletb.png").convert_alpha()
explosion_images = [pygame.image.load(f"assets/images/explosion{i}.png").convert_alpha() for i in range(1, 6)]
plane_image = pygame.image.load("assets/images/f14.png").convert_alpha()
engine_sound = pygame.mixer.Sound("assets/sounds/engine.mp3")
explosion_sound = pygame.mixer.Sound("assets/sounds/explosion.mp3")
missile_sound = pygame.mixer.Sound("assets/sounds/missile.mp3")  # Load missile sound
fail_sound = pygame.mixer.Sound("assets/sounds/fail.mp3")  # Load fail sound
background_music = pygame.mixer.music.load("assets/sounds/bgmusic.mp3")  # Background music

# Resize images
missile_width, missile_height = 100, 120
plane_width, plane_height = 90, 90
explosion_width, explosion_height = 150, 150  # Explosion is larger to cover the plane

missile_image = pygame.transform.scale(missile_image, (missile_width, missile_height))
plane_image = pygame.transform.scale(plane_image, (plane_width, plane_height))
explosion_images = [pygame.transform.scale(img, (explosion_width, explosion_height)) for img in explosion_images]

# Game variables
missiles = []
cooldown = 0
score = 0
missile_speed = 5
plane_speed = 7
plane_speed_boost = 14
explosion_timer = 0
explosion_frame = 0
explosion_position = None
plane_rect = pygame.Rect(width // 2 - plane_width // 2, height - plane_height - 10, plane_width, plane_height)

# Play background music continuously
pygame.mixer.music.play(-1)


# Function to spawn a missile at a random position at the top
def spawn_missile():
    x = random.randint(0, width - missile_width)
    y = -missile_height  # Start the missile above the screen
    missiles.append([x, y])
    missile_sound.play()  # Play missile sound when a missile appears


# Function to handle missile movement and collision with the plane
def handle_missiles():
    global score, cooldown, explosion_timer, explosion_frame, explosion_position, missile_speed
    for missile in missiles[:]:
        missile[1] += missile_speed  # Move the missile down by increasing its y-coordinate
        missile_rect = pygame.Rect(missile[0], missile[1], missile_width, missile_height)
        if missile_rect.colliderect(plane_rect):  # Hit the plane
            missiles.remove(missile)
            explosion_sound.play()
            fail_sound.play()  # Play fail sound on collision
            # Center the explosion image on the plane's position
            explosion_position = (
                plane_rect.centerx - explosion_width // 2,
                plane_rect.top - explosion_height // 2
            )
            explosion_frame = 0
            explosion_timer = 30  # Show explosion for 30 frames
            cooldown = 100  # Set cooldown time
        elif missile[1] > height:  # Missed the plane, increase score
            missiles.remove(missile)
            score += 1
            missile_speed = 5 + score // 5  # Increase speed as score increases


# Function to move the plane based on user input
def move_plane():
    global plane_speed
    keys = pygame.key.get_pressed()

    # Movement with acceleration for smoothness
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # Move left
        plane_rect.x -= plane_speed
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Move right
        plane_rect.x += plane_speed
    if keys[pygame.K_UP] or keys[pygame.K_w]:  # Move up
        plane_rect.y -= plane_speed
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:  # Move down
        plane_rect.y += plane_speed

    # Ensure the plane stays within screen bounds
    if plane_rect.left < 0:
        plane_rect.left = 0
    if plane_rect.right > width:
        plane_rect.right = width
    if plane_rect.top < 0:
        plane_rect.top = 0
    if plane_rect.bottom > height:
        plane_rect.bottom = height


# Function to handle events
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
    return True


# Function to show game over screen
def game_over_screen():
    window.fill((0, 0, 0))
    font = pygame.font.Font(None, 74)
    text = font.render("GAME OVER", True, (255, 0, 0))
    window.blit(text, (width // 2 - text.get_width() // 2, height // 3))

    font = pygame.font.Font(None, 50)
    try_again_text = font.render("Try Again", True, (255, 255, 255))
    exit_text = font.render("Exit", True, (255, 255, 255))

    try_again_button = pygame.Rect(width // 2 - 100, height // 2, 200, 50)
    exit_button = pygame.Rect(width // 2 - 100, height // 2 + 60, 200, 50)

    pygame.draw.rect(window, (0, 0, 255), try_again_button)
    pygame.draw.rect(window, (0, 0, 255), exit_button)

    window.blit(try_again_text, (width // 2 - try_again_text.get_width() // 2, height // 2 + 5))
    window.blit(exit_text, (width // 2 - exit_text.get_width() // 2, height // 2 + 65))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if try_again_button.collidepoint(event.pos):
                    return True  # Restart the game
                if exit_button.collidepoint(event.pos):
                    return False  # Exit the game


# Main game loop
running = True
clock = pygame.time.Clock()
spawn_timer = 0

while running:
    clock.tick(30)
    window.blit(background, (0, 0))

    # Handle missile movement and collision detection
    handle_missiles()

    # Move the plane based on user input
    move_plane()

    # Draw missiles
    for missile in missiles:
        window.blit(missile_image, (missile[0], missile[1]))

    # Draw explosion if timer is active
    if explosion_timer > 0:
        window.blit(explosion_images[explosion_frame], explosion_position)
        explosion_timer -= 1
        if explosion_timer % 6 == 0:  # Change frame every 6 ticks
            explosion_frame = (explosion_frame + 1) % len(explosion_images)
        if explosion_timer == 0:
            running = game_over_screen()
            if not running:
                break
            # Reset game variables
            missiles.clear()
            score = 0
            missile_speed = 5
            plane_rect.x = width // 2 - plane_width // 2
            plane_rect.y = height - plane_height - 10

    # Draw the plane only if there is no active explosion
    if explosion_timer == 0:
        window.blit(plane_image, plane_rect.topleft)

    # Display score
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(score_text, (10, 10))

    # Spawn missiles periodically
    spawn_timer += 1
    if spawn_timer >= 30:  # Spawn a new missile every 30 frames (adjust as needed)
        spawn_missile()
        spawn_timer = 0

    # Event handling
    running = handle_events()

    pygame.display.flip()

pygame.quit()
