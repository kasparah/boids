# import classes as c
import settings as s
import pygame as pg
import sys
import classes
import os
from spritesheet_loader import sprite_sheet
import pygame_gui
from pygame_gui.elements import UIHorizontalSlider

# Initialize pygame
pg.init()

# Creating a UImanager object
ui_manager = pygame_gui.UIManager((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
# Creating slider object
separation_slider = UIHorizontalSlider(
    relative_rect=pg.Rect((10,10), (200, 20)),  # Size of slider and position
    start_value=s.SEPARATION_FACTOR,            # Starting value of slider
    value_range=(0.0,1.0),                      # Slider value range
    manager=ui_manager                          # The manager of this slider

)
# With these two lines we get access to the folder our current file is in
# use this to later access our images and other files that are needed.
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "image")
      
# Dimension of screen object
screen = pg.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
# Create title on window
pg.display.set_caption(s.TITLE)
# Background
background = pg.Surface(screen.get_size())
background = background.convert()
background.fill(s.BG_COLOR)

# Image folder
img_dir = os.path.join(os.path.dirname(__file__), 'image')
# Using function to return a list with all individual images from spritesheet
bird_list = sprite_sheet((30,30), os.path.join(img_dir, "bird_2_blue.png"))
hoik_list = sprite_sheet((30,30), os.path.join(img_dir, "hoik.png"))
boid_img = bird_list[0]
hoik_img = hoik_list[5]
obstacle_img = pg.image.load(os.path.join(img_dir, 'Rock Pile.png')).convert_alpha()

# Creating object instances
all_sprites = pg.sprite.RenderPlain()
boid_sprites = pg.sprite.RenderPlain()
obstacle = classes.Obstacle(obstacle_img)
all_sprites.add(obstacle)
for i in range(100):
    i = classes.Boid(boid_img, all_sprites, boid_sprites)
    boid_sprites.add(i)                       # Add list of all boids to each boid

all_sprites.add(boid_sprites)
# hoik = classes.Hoik(hoik_img, all_sprites)
# all_sprites.add(hoik)
clock = pg.time.Clock() # Will use clock to limit how fast the code runs. 
if __name__ == "__main__":
    running = True
    # game loop
    while running:
        time_delta = clock.tick(s.FPS) / 1000.0     # GUI manager uses timer
        clock.tick(s.FPS)
        for event in pg.event.get():
            # Quit simulation either by clicking on exit or pressing 'q'.
            if event.type == pg.QUIT: 
                running = False
                pg.quit()
                sys.exit()
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    sys.exit()
            # This handles the slider
            elif event.type == pg.USEREVENT:
                if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == separation_slider:
                        s.SEPARATION_FACTOR = event.value   # Changes separation factor
                        print(s.SEPARATION_FACTOR)
            ui_manager.process_events(event)
      
        # Update
        all_sprites.update()
        ui_manager.update(time_delta)

        # Draw
        screen.blit(background, (0,0))
        all_sprites.draw(screen)
        ui_manager.draw_ui(screen)
        pg.display.flip()

      
        # Update screen
        pg.display.flip()
    