import pygame as pg
import settings as s
from random import randint
from math import hypot
from math import sqrt
from math import atan2, cos, sin

class Drawable_object(pg.sprite.Sprite):
    """An object that is drawable."""
    def __init__(self, img):
        pg.sprite.Sprite.__init__(self)
        self.image = img                # Image from file
        # Need to get image's rect in order to change it's coordinates
        self.rect = self.image.get_rect()
        self.pos = pg.math.Vector2()

class Moving_object(Drawable_object):
    """An object that can move. Spawn object with random coordinates. 
        The object will wrap around screen edges. """
    def __init__(self, img, allsprites):
        super().__init__(img)
        self.allsprites = pg.sprite.Group()   # All sprites in game
        self.allsprites = allsprites
        screen = pg.display.get_surface()       
        self.window = screen.get_rect()     # Class gets access to screen
        # Make starting position of object be random
        # Position can't include 0, if not using wrap around method
        self.pos.x = randint(self.rect.width+1, s.SCREEN_WIDTH-self.rect.width-1)
        self.pos.y = randint(self.rect.height+1, s.SCREEN_HEIGHT-self.rect.height-1)
        # Object's center is where it is on screen
        self.rect.center = self.pos
        # Arbitrary starting value for velocity
        self.vel = pg.math.Vector2(2, 2)
        # How fast the object can turn, increase value to increase turning speed
        self.turnfactor = 0.8
        self.avoid_range = 50   # When to avoid obstacle

    def update(self):
        """Updates object on screen. Turning object if it is near screen edges.
          Object's velocity is limited. """
        # Here if object is 100 pixels away from any screen edges, make it turn
        if self.rect.left < 50:
            self.vel.x += self.turnfactor
        if self.rect.right > s.SCREEN_WIDTH - 50:
            self.vel.x -= self.turnfactor
        if self.rect.top < 50:
            self.vel.y += self.turnfactor
        if self.rect.bottom > s.SCREEN_HEIGHT - 50:
            self.vel.y -= self.turnfactor

        # Wrap around screen
        self.wrap_around()
        self.avoid_obstacle()
        # Limit the object's velocity
        self.vel.scale_to_length(min(s.MAX_SPEED, self.vel.length()))
     
        self.move()
    def wrap_around(self):
        """Wraps object around the screen if it goes past edge of screen border."""
        # If right side of object is past left side of screen, make the object's left be the right
        # side of screen. This makes it looks like it wraps around. Similar logic to top and bottom. 
        if self.rect.right < 0:
            self.rect.left = s.SCREEN_WIDTH
        elif self.rect.left > s.SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.bottom < 0:
            self.rect.top = s.SCREEN_HEIGHT
        elif self.rect.top > s.SCREEN_HEIGHT:
            self.rect.bottom = 0

    def move(self):
        """Update the object's position vector with velocity vector."""
        self.pos += self.vel
        self.rect = self.rect.move(self.vel)    # Moving image '
    
    def distance(self, other):
        """Returns the euclidean distance between two vectors."""
        # result = hypot(other.rect.x - self.rect.x, other.rect.y - self.rect.y)
        # Using object's center value to get proper turning. If using object's position vector
        # then object will turn too late, resulting in images 'crashing'. 
        result = hypot(other.rect.center[0] - self.rect.center[0], other.rect.center[1] - self.rect.center[1])
        return result - (self.rect.width + other.rect.width) / 2    # Dont want to include width
    
    def avoid_obstacle(self):
        """Method to move away obstacle. """
        for sprite in self.allsprites:
            if isinstance(sprite, Obstacle):
                if self.distance(sprite) < self.avoid_range:
                    self.vel.x += self.turnfactor
                    self.vel.y += self.turnfactor
                    
class Boid(Moving_object):
    """Bird-like object that will move according to its flock. If too near another boid, steer away.
    Will try to move in same direction as its local flock, and match its speed."""
    def __init__(self, img, allsprites, flock):
        super().__init__(img, allsprites)
        self.image = img
        self.allsprites = pg.sprite.Group()     # All sprites in game
        self.allsprites = allsprites   
        self.local_flock = pg.sprite.Group()    # All boids
        self.local_flock =flock                  
        self.acceleration = pg.math.Vector2()
        self.close_range = 8                    
        self.long_range = 40                            # The boid's 'visual range'
        self.seperation_factor = s.SEPARATION_FACTOR    # How much to separate from other boids
        self.alignment_factor = s.ALIGNMENT_FACTOR      # How much to match other boid's velocity
        self.cohesion_factor = s.COHESION_FACTOR        # How much to steer to near flock's avg position

    def update(self):
        """Update boid's movement and position using separation, alignment and cohesion."""
        self.separation()
        self.alignment()
        # Using acceleration to avoid boids becoming stationary (if using vel in alignment)
        self.vel += self.acceleration
        self.acceleration *= 0
        self.cohesion()
        return super().update() # Includes parent update method
    
    def separation(self):
        """When another boid is too close, steer away."""
        v = pg.math.Vector2()   # This will be vector we add all other boid positions to 
        for boid in self.local_flock:   # Checking every boid in simulation
            if boid == self:
                continue
            if self.distance(boid) < self.close_range:
                # If other boid is too close, add it's position to a vector
                v += boid.pos - self.pos
        # After checking all boids in close range, add a value to boid's velocity to steer away
        self.vel += v*self.seperation_factor
            
    def alignment(self):
        """Boid will try to match the velocities of their neighbors."""
        v = pg.math.Vector2()   # Will be sum of velocity of all boids in local range
        count = 0               # Keep track of how many boids in local range
        for boid in self.local_flock:
            if boid == self:
                   continue
            if self.distance(boid) < self.long_range:
                v += boid.vel
                count += 1
        if count > 1:           # Can't divide by zero
            v.x = v.x / (count)
            v.y = v.y / (count)
            # Using acceleration attribute, or else if using self.vel the boid would become
            # stationary.
            self.acceleration = (v-self.vel) * self.alignment_factor    
        
    def cohesion(self):
        """Boids will steer towards the center of mass of other boids within range."""
        neighbor_boids = 0      # Number of boids nearby
        avg_pos = pg.math.Vector2()
        # Store sum of all positions of other boids in local range, and num of boids
        for boid in self.local_flock:
            if boid == self:
                   continue # Skip This
            if self.distance(boid) < self.long_range:
                avg_pos += boid.pos
                neighbor_boids += 1
        if neighbor_boids > 0:
            avg_pos /= neighbor_boids               # Get avg position
        cohesion_vector = avg_pos - self.pos        # Exclude this boid's position
        cohesion_distance = cohesion_vector.length()# Get vector length of avg position of boids   
        if cohesion_distance < self.long_range:     # If the avg position of boids is within local range
            self.vel += cohesion_vector*self.cohesion_factor    # Then we add a value to self.velocity


class Hoik(Moving_object):
    """A predator object that will hunt down boids."""
    def __init__(self, img, allsprites):
        super().__init__(img, allsprites)
        self.image = img
        self.allsprites = pg.sprite.Group(allsprites)
        self.chase_range = s.CHASE_RANGE
        self.target_group = pg.sprite.Group()
        self.target_list = self.target_group.sprites()  # List
    
    def update(self):
        if len(self.target_list) == 0:
            self.get_target()
        self.chase()
        for sprite in self.allsprites:
            if isinstance(sprite, Boid):
                if pg.Rect.colliderect(self.rect, sprite.rect):
                    sprite.kill()
                    self.target_list.clear()
                    print("Target neutralized")
        return super().update()
    
    def get_target(self):
        # To chase a boid, we need to find a boid, then get its position
       # after that we need to move hoik gradually to this boid. 
        if len(self.target_list) == 0:  # Only find new target if out of targets
            for sprite in self.allsprites:
                if isinstance(sprite, Boid):
                    if self.distance(sprite) < self.chase_range:
                        self.target_list.append(sprite)
                        print("Target acquired")
        else:
            return
    def chase(self):
        """Chase nearby boids until they are killed."""
        if len(self.target_list) == 0:
            return
        
        # Calculate predicted future position of target
        target = self.target_list[0]
        time_to_target = (target.pos - self.pos).length() / s.MAX_SPEED
        future_target_pos = target.pos + target.vel * time_to_target
        
        # Calculate desired velocity towards predicted target position
        desired_vel = future_target_pos - self.pos
        if desired_vel.length() == 0:   # To avoid ValueError, cannot scale vector with zero length
            return
        desired_vel.normalize()
        desired_vel *= s.MAX_SPEED
        
        # Calculate steering force and apply it
        steering = desired_vel - self.vel
        if steering.length() == 0:  # To avoid ValueError, cannot scale vector with zero length
            return 
        steering.scale_to_length(min(s.MAX_FORCE, steering.length()))
        self.vel += steering
        self.vel.scale_to_length(min(s.MAX_SPEED, self.vel.length()))

class Obstacle(Drawable_object):
    """An object the boids will have to avoid."""
    def __init__(self, img):
        super().__init__(img)
        self.image = img
        self.pos = pg.math.Vector2(100,20)  # position on screen
        self.rect.topleft = self.pos 
