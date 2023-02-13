#  Call of Duty: Korean War by Jerry Cui
#  Top-down 2D shooter game

#  Import modules needed
import pygame
from sys import exit
from random import randrange, choice, randint
import math

# Start-up stuff
# Start up Pygame
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Constants
# Screen
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60  # Frames per second

# Game constants
HEALTH_REGEN_TIME = FPS * 1.5
GRENADE_COOLDOWN = FPS * 2

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GLITCH_COLOR = (71, 112, 76)  # A lot of PNG images have this color in their background for some reason

# Pygame stuff
display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)  # Full screen mode
pygame.display.set_caption("Korean War")
clock = pygame.time.Clock()

# Load images
# Player images aren't in the right dimensions, so I scale them into the right size
player_walk_images = [pygame.transform.scale(pygame.image.load(r"animations\player\player_walk_0.png"), (32, 42)),
                      pygame.transform.scale(pygame.image.load(r"animations\player\player_walk_1.png"), (32, 42)),
                      pygame.transform.scale(pygame.image.load(r"animations\player\player_walk_2.png"), (32, 42)),
                      pygame.transform.scale(pygame.image.load(r"animations\player\player_walk_3.png"), (32, 42))]

american_walk_images = [pygame.image.load(r"animations\enemy\enemy_animation_0.png"),
                        pygame.image.load(r"animations\enemy\enemy_animation_1.png"),
                        pygame.image.load(r"animations\enemy\enemy_animation_2.png"),
                        pygame.image.load(r"animations\enemy\enemy_animation_3.png")]

dog_images = [pygame.image.load(r"animations\enemy\dog\dog1.png"),
              pygame.image.load(r"animations\enemy\dog\dog2.png"),
              pygame.image.load(r"animations\enemy\dog\dog3.png"),
              pygame.image.load(r"animations\enemy\dog\dog4.png")]

tank_images = [pygame.image.load(r"animations\enemy\tank\tank.png")]

sniper_images = [pygame.image.load(r"animations\enemy\sniper\enemy_animation_0.png"),
                 pygame.image.load(r"animations\enemy\sniper\enemy_animation_1.png"),
                 pygame.image.load(r"animations\enemy\sniper\enemy_animation_2.png"),
                 pygame.image.load(r"animations\enemy\sniper\enemy_animation_3.png")]

rocket = pygame.image.load(r"objects\rocket.png").convert()
rocket.set_colorkey(GLITCH_COLOR)  # Remove this color from the image
grenade = pygame.image.load(r"weapons\grenade.png").convert()
grenade.set_colorkey(GLITCH_COLOR)
explosion = pygame.image.load(r"objects\explosion.png").convert()
explosion.set_colorkey(GLITCH_COLOR)
hitmarker = pygame.image.load(r"objects/hitmarker.png").convert()
hitmarker.set_colorkey(WHITE)
hitmarker.set_colorkey(BLACK)
main_menu_image = pygame.image.load(r"menus\main_menu.png").convert()
settings_on_on = pygame.image.load(r"menus\settings_on_on.png").convert()
settings_on_off = pygame.image.load(r"menus\settings_on_off.png").convert()
settings_off_on = pygame.image.load(r"menus\settings_off_on.png").convert()
settings_off_off = pygame.image.load(r"menus\settings_off_off.png").convert()

# Font types
hud_font = pygame.font.Font("freesansbold.ttf", 16)
small_hud_font = pygame.font.Font("freesansbold.ttf", 10)
bigger_hud_font = pygame.font.Font("freesansbold.ttf", 24)

# Sound
gunfire = pygame.mixer.Sound(r"sound\gunfire.wav")
hitmarker_sound = pygame.mixer.Sound(r"sound\hitmarker.wav")
enemy_gunfire = pygame.mixer.Sound(r"sound\enemy_gunfire.wav")
rocket_launch = pygame.mixer.Sound(r"sound\launch.wav")
explosion_sound = pygame.mixer.Sound(r"sound\explosion.wav")
game_music = pygame.mixer.Sound(r"sound\game_music.wav")
defeat_music = pygame.mixer.Sound(r"sound\defeat_music.mp3")
menu_music = pygame.mixer.Sound(r"sound\menu_music.mp3")

# Each time the player dies, a quote is displayed
death_quotes = [
    "We cannot let this, we’ve never allowed any crisis from the Civil War straight through to the pandemic of 17, "
    "all the way around, 16, we have never, never let our democracy sakes second fiddle, way they, we can both have a "
    "democracy and correct the public health. - Joe Biden",
    "Sometimes by losing the battle, you find a new way to win the war. - Donald Trump",
    "Women have always been the primary victims of war. - Hillary Clinton",
    "I'm not opposed to all wars. I'm opposed to dumb wars. - Barack Obama",
    "I just want you to know that, when we talk about war, we're really talking about peace. - George W. Bush Jr.",
    "We must teach our children to resolve their conflicts with words, not weapons. - Bill Clinton"
]

# Settings
music = True
sound_fx = True


# Sound Channels:
# Channel(0) is used to play the sound effect for player bullets
# Channel(1) is used to play the sound effect for enemy bullets
# Channel(2) is used to play the hitmarker sound effect
# Channel(3) is used to play the sound effect when a rocket is launched
# Channel(4) is used to play explosion sound effects
# Channel(5) is used to play background music
# Channel(6) is used to play enemy rocket launches


# Objects
class Player:
    def __init__(self, x, y, width, height, primary_weapon, secondary_weapon):
        """ (Player, int, int, int, int, Gun, Gun) -> None
            Creates the player object
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.primary_weapon = primary_weapon
        self.secondary_weapon = secondary_weapon

        self.animation_count = 0
        self.moving_right = False
        self.moving_left = False
        self.health = 100
        self.health_regen_timer = 90
        self.money = 0

        self.hitbox = pygame.Rect(x, y, width, height)  # This is the hitbox of the player

        self.grenades = 4  # How many grenades this player has
        self.c4_inventory = 10  # How many C4 this player has
        self.armour = 200

        self.grenade_cooldown = FPS * 2  # How many frames remaining until the player can throw another grenade
        self.c4_cooldown = FPS * 2  # How many frames remaining until the player can deploy another C4

        self.hitmarker_chain = 0  # How many more frames to display a hitmarker for
        self.kills = 0

        self.in_tutorial = False  # Health regeneration is different in the tutorial

    def handle_weapons(self):
        """ (Player) -> None
            Draws the weapon onto the player using complex geometry
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()  # Get mouse position

        # Determine the angle to rotate the gun to
        rel_x, rel_y = mouse_x - self.x, mouse_y - self.y  # The coordinates of the mouse location, if we treat the
        # player as (0, 0)
        # atan2(x, y) returns the angle formed by a line from (0, 0) to (x, y) and the x-axis. However, it is confined
        # to (-pi, pi) for some reason, so in order to make it actually work, I multiplied it by some numbers. This made
        # it able to rotate in a full circle, but it still wouldn't point towards the mouse. So I used trial and error
        # until I tried (180 / pi), which worked. This rotated it at the right ratio, but it was always reflected
        # across the x-axis first, so I added a negative sign, which fixed it.
        angle = -((180 / math.pi) * math.atan2(rel_y, rel_x))
        # For the coordinates, we take into account the image offset and the dimensions of the gun image
        gun_x = self.x + self.primary_weapon.x_offset - int(self.primary_weapon.image.get_width() / 2)
        gun_y = self.y + self.primary_weapon.y_offset - int(self.primary_weapon.image.get_height() / 2)

        display.blit(pygame.transform.rotate(self.primary_weapon.image, angle), (gun_x, gun_y))  # Display the gun

    def swap_weapon(self):
        """ (Player) -> None
            Swaps the two guns that the player is holding
        """
        self.primary_weapon, self.secondary_weapon = self.secondary_weapon, self.primary_weapon

    def main(self):
        """ (Player) -> None
            Displays the player onscreen and processes events that happened to the player
        """

        # 1. Set which frame of animation to use for the player
        # There are four images, which each stay for four frames each-
        if self.animation_count + 1 >= len(player_walk_images * 4):
            self.animation_count = 0
        self.animation_count += 1

        # 2. Draw the image of the player on the screen
        if self.moving_right:
            display.blit(player_walk_images[self.animation_count // 4], (self.x, self.y))
        elif self.moving_left:  # Image will be flipped if the player is moving left
            display.blit(pygame.transform.flip(player_walk_images[self.animation_count // 4], True, False), (self.x,
                                                                                                             self.y))
        else:  # Image will use the default frame if the player is not moving
            display.blit(pygame.transform.scale(player_walk_images[0], (32, 42)), (self.x, self.y))

        # 3. Now that the player has moved, update its hitbox
        self.hitbox = pygame.Rect(self.x, self.y, 32, 42)

        # 4. Reset the variables that determined the player's direction
        self.moving_right = False
        self.moving_left = False

        # 5. Call the function to draw weapon onto screen
        self.handle_weapons()

        # 6. Regenerate the player's health, up to 100. In the tutorial, the player has 1000 health, so it will regen
        # up to 1000.
        if self.in_tutorial:
            max_health = 1000
        else:
            max_health = 100

        if self.health < max_health:
            self.health_regen_timer -= 1
            if self.health_regen_timer == 0:
                self.health_regen_timer = HEALTH_REGEN_TIME
                self.health += 10
                if self.health > max_health:
                    self.health = max_health

        # 7. Increment cool-downs (grenades + C4 placement, and hit markers)
        if self.grenade_cooldown != 0:
            self.grenade_cooldown -= 1

        if self.c4_cooldown != 0:
            self.c4_cooldown -= 1

        if self.hitmarker_chain > 0:
            self.hitmarker_chain -= 1

        # 8. Use body armour to take damage, by resetting player health to 100 by taking away armour hit points
        # If the player has 20 body armour, but takes 80 damage, the body armour becomes 0, but the player's health is
        # still 100. The armour is supposed to tank all damage while it is on
        if self.health < 100:
            if self.armour > 0:
                damage_taken = 100 - self.health
                self.health = 100
                self.armour -= damage_taken
                if self.armour < 0:
                    self.armour = 0

        # 9. If the player ran out of ammo in weapon, try reloading automatically.
        if self.primary_weapon.magazine_ammo == 0:
            if self.primary_weapon.reserve_ammo > 0:
                if not self.primary_weapon.reloading:
                    self.primary_weapon.reload()

    def throw_grenade(self):
        """ (Player) -> None
            Throw a grenade
        """

        mouse_x, mouse_y = pygame.mouse.get_pos()
        grenades.append(Grenade(self.x, self.y, mouse_x, mouse_y, sks, 0))  # Throw a grenade in direction of mouse

        self.grenade_cooldown = FPS * 2  # Set the cooldown


class Gun:
    def __init__(self, **kwargs):
        """ (Gun, str, tuple, int, int, int, str, float, float, int, int, int, int, float, float, str) -> None
            Create a Gun object. I'm using **kwargs because there's a lot of arguments, so having the argument name
            makes it easier to edit the object. Should be self-explanatory what is for what
        """
        self.image = pygame.image.load(kwargs["image_string"]).convert()
        self.image.set_colorkey(kwargs["colorkey"])  # Color of image background to remove
        self.damage = kwargs["damage"]
        self.magazine_capacity = kwargs["magazine_capacity"]
        self.reserve_capacity = kwargs["reserve_capacity"]
        self.name = kwargs["name"]
        self.chambered_reload_time = kwargs["chambered_reload_time"]  # Reload time if magazine is not empty vs
        self.empty_reload_time = kwargs["empty_reload_time"]  # reload time if the magazine is empty
        self.x_offset = kwargs["x_offset"]  # How far off from the player the gun is drawn so that it looks like the
        self.y_offset = kwargs["y_offset"]  # player is drawing it correctly
        self.range = kwargs["range"]
        self.bullet_speed = kwargs["bullet_speed"]
        self.magazine_ammo = kwargs["magazine_capacity"]
        self.reserve_ammo = kwargs["reserve_capacity"]
        self.fire_delay = kwargs["fire_delay"]  # How long between shots (applies to automatic weapons only, basically)
        self.fire_mode = kwargs["fire_mode"]  # semi_automatic (one click = one bullet) or automatic (hold down mouse)
        self.fire_delay_ticker = kwargs["fire_delay"]

        self.reloading = False
        self.frames_remaining = 0  # Frames left until a reload is finished, set to 0 for now

    def reload(self):
        """ (Gun) -> None
            Initializes a reload
        """
        if self.magazine_ammo == 0:  # Reloading takes faster if there is no bullet already in the gun
            self.frames_remaining = round(self.empty_reload_time * FPS)  # Number of frames to finish reload
        else:
            self.frames_remaining = round(self.chambered_reload_time * FPS)

        self.reloading = True

    def main(self):
        """ (Gun) -> None
            Handles its responsibilities (drawing the gun is handled by the Player class). That means that if it is
            reloading, count down the number of frames left by 1
        """
        if self.reloading:
            # Decrease frames left until finished reload by one, and finish it if it reaches 0
            self.frames_remaining -= 1
            if self.frames_remaining == 0:
                magazine_ammo = self.magazine_ammo
                if self.reserve_ammo >= self.magazine_capacity:
                    self.reserve_ammo -= self.magazine_capacity - magazine_ammo
                    self.magazine_ammo = self.magazine_capacity
                else:
                    self.magazine_ammo = self.reserve_ammo
                    self.reserve_ammo = 0
                self.reloading = False


#  Create all the Gun objects
sks = Gun(image_string=r"weapons\sks.png", colorkey=(71, 112, 76), damage=60, magazine_capacity=20,
          reserve_capacity=120, name="Samozaryadny Karabiner Sistemy Simonova (SKS)", chambered_reload_time=2.4,
          empty_reload_time=2.8, x_offset=30, y_offset=25, range=12, bullet_speed=45, fire_delay=0.3,
          fire_mode="semi_automatic")
ak47 = Gun(image_string=r"weapons\ak47.png", colorkey=(71, 112, 76), damage=50, magazine_capacity=30,
           reserve_capacity=180, name="Kalashnikov 1947 (AK47)", chambered_reload_time=2.6, empty_reload_time=3.1,
           x_offset=30, y_offset=25, range=12, bullet_speed=45, fire_delay=12, fire_mode="automatic")
mauserc96 = Gun(image_string=r"weapons\mauserc96.png", colorkey=(71, 112, 76), damage=25, magazine_capacity=10,
                reserve_capacity=60, name="Mauser Construktion 96", chambered_reload_time=1.6, empty_reload_time=1.9,
                x_offset=20, y_offset=25, range=8, bullet_speed=45, fire_delay=0.1, fire_mode="semi_automatic")
m1carbine = Gun(image_string=r"weapons\m1carbine.png", colorkey=(71, 112, 76), damage=45, magazine_capacity=15,
                reserve_capacity=90, name="M1 Carbine", chambered_reload_time=2.6, empty_reload_time=2.9, x_offset=32,
                y_offset=25, range=12, bullet_speed=45, fire_delay=12, fire_mode="semi_automatic")
m1911 = Gun(image_string=r"weapons\m1911.png", colorkey=(255, 255, 255), damage=30, magazine_capacity=7,
            reserve_capacity=42, name="Colt M1911", chambered_reload_time=1.6, empty_reload_time=1.8, x_offset=25,
            y_offset=30, range=8, bullet_speed=45, fire_delay=10, fire_mode="semi_automatic")
ithaca37 = Gun(image_string=r"weapons\ithaca37.png", colorkey=(71, 112, 76), damage=90, magazine_capacity=5,
               reserve_capacity=30, name="Ithaca Model 37 Shotgun", chambered_reload_time=5, empty_reload_time=5,
               x_offset=25, y_offset=30, range=5, bullet_speed=45, fire_delay=12, fire_mode="semi_automatic")
springfield = Gun(image_string=r"weapons\springfield.png", colorkey=(0, 0, 0), damage=95, magazine_capacity=5,
                  reserve_capacity=30, name="M1903 Springfield Sniper Rifle", chambered_reload_time=3.2,
                  empty_reload_time=5, x_offset=25, y_offset=30, range=100, bullet_speed=45, fire_delay=15,
                  fire_mode="semi_automatic")
mosin_nagant = Gun(image_string=r"weapons\mosin_nagant.png", colorkey=(0, 0, 0), damage=150, magazine_capacity=5,
                   reserve_capacity=30, name="Mosin Nagant Sniper Rifle", chambered_reload_time=3,
                   empty_reload_time=3.3, x_offset=27, y_offset=27, range=100, bullet_speed=45, fire_delay=2.8,
                   fire_mode="semi_automatic")
m3 = Gun(image_string=r"weapons\m3.png", colorkey=(71, 112, 76), damage=30, magazine_capacity=30, reserve_capacity=180,
         name="United States Submachine Gun, Cal. .45, M3", chambered_reload_time=3, empty_reload_time=3.4, x_offset=25,
         y_offset=30, range=10, bullet_speed=45, fire_delay=8, fire_mode="automatic")
type50 = Gun(image_string=r'weapons\type50.png', colorkey=(71, 112, 76), damage=30, magazine_capacity=35,
             reserve_capacity=245, name="PPSh-41 Type 50 Submachine Gun Box Magazine", chambered_reload_time=3.4,
             empty_reload_time=3.6, x_offset=30, y_offset=30, range=9, bullet_speed=45, fire_delay=5,
             fire_mode="automatic")
bren = Gun(image_string=r"weapons\bren.png", colorkey=(71, 112, 76), damage=35, magazine_capacity=100,
           reserve_capacity=600, name="Bren L4 Light Machine Gun", chambered_reload_time=9.86, empty_reload_time=11,
           x_offset=35, y_offset=28, range=12, bullet_speed=45, fire_delay=9, fire_mode="automatic")
dp27 = Gun(image_string=r"weapons\dp27.png", colorkey=(71, 112, 76), damage=25, magazine_capacity=100,
           reserve_capacity=600, name="Degtyaryov DP-27 Type 53 Light Machine Gun", chambered_reload_time=4.7,
           empty_reload_time=5.6, x_offset=35, y_offset=28, range=12, bullet_speed=45, fire_delay=8,
           fire_mode="automatic")
bazooka = Gun(image_string=r"weapons\bazooka.png", colorkey=(71, 112, 76), damage=0, magazine_capacity=1,
              reserve_capacity=6, name="M20 Super Bazooka", chambered_reload_time=4, empty_reload_time=4, x_offset=35,
              y_offset=28, range=100, bullet_speed=6, fire_delay=45, fire_mode="semi_automatic")
rpg7 = Gun(image_string=r"weapons\rpg7.png", colorkey=(71, 112, 76), damage=0, magazine_capacity=1, reserve_capacity=6,
           name="Ruchnoy Protivotankoviy Granatomyot 7 Rocket Launcher (RPG-7)", chambered_reload_time=4,
           empty_reload_time=4, x_offset=35, y_offset=28, range=100, bullet_speed=6, fire_delay=45,
           fire_mode="semi_automatic")
tank_turret = Gun(image_string=r"weapons\bazooka.png", colorkey=(71, 112, 76), damage=0, magazine_capacity=1,
                  reserve_capacity=6, name="Tank Turret", chambered_reload_time=4, empty_reload_time=4, x_offset=110,
                  y_offset=55, range=60, bullet_speed=9, fire_delay=45, fire_mode="semi_automatic")
test_weapon = Gun(image_string=r"weapons\dp27.png", colorkey=(71, 112, 76), damage=99999999,
                  magazine_capacity=99999999999999999, reserve_capacity=999999999999999999999, name="Test Weapon",
                  chambered_reload_time=1, empty_reload_time=1, x_offset=28, y_offset=12, range=45, bullet_speed=8,
                  fire_delay=4, fire_mode="automatic")


class Bullet:
    def __init__(self, x, y, mouse_x, mouse_y, gun, damage):
        """ (Bullet, int, int, int, int, Gun, int) -> None
            Create the Bullet object. This is w
        """
        self.x = x
        self.y = y
        self.mouse_x = mouse_x  # In the case of enemy fired bullets, this is the target coordinate
        self.mouse_y = mouse_y
        self.speed = gun.bullet_speed
        self.angle = math.atan2(y - mouse_y, x - mouse_x)  # Used to rotate rockets
        self.x_vel = math.cos(self.angle) * self.speed
        self.y_vel = math.sin(self.angle) * self.speed
        self.range = gun.range
        self.damage = damage

        self.hitbox = pygame.Rect(self.x, self.y, 8, 8)
        self.type = "Bullet"

    def main(self):
        """ (Bullet) -> None
            If the bullet has not reached its maximum range, then keep going, otherwise, do nothing
        """
        self.range -= 1

        if not self.range < 0:
            self.x -= int(self.x_vel)
            self.y -= int(self.y_vel)

            pygame.draw.circle(display, BLACK, (self.x, self.y), 4)

            self.hitbox = pygame.Rect(self.x, self.y, 8, 8)


class Rocket(Bullet):
    def __init__(self, x, y, mouse_x, mouse_y, gun, damage):
        """ (Rocket, int, int, int, int, Gun, int) -> None
            Create the Rocket object, a slower-moving bullet that explodes upon impact.
        """
        super().__init__(x, y, mouse_x, mouse_y, gun, damage)
        self.death_radius = pygame.Rect(self.x - 50, self.y - 50, 100, 100)  # Kills all enemies in here
        self.damage_radius = pygame.Rect(self.x - 100, self.y - 100, 200, 200)  # Damages all enemies in here
        self.type = "Rocket"

        self.exploding = False
        self.exploding_timer = FPS  # An explosion stays visible for one second

    def main(self):
        """ (Rocket) -> None
            Same as Bullet main, it will draw an explosion after it explodes for one second. This explosion will still
            damage enemies inside the area while
        """
        self.range -= 1

        if self.range > 0:
            if not self.exploding:
                self.x -= int(self.x_vel)
                self.y -= int(self.y_vel)

                rel_x, rel_y = self.x - int(self.x_vel) - self.x, self.y - int(self.y_vel) - self.y
                angle = -((180 / math.pi) * math.atan2(rel_y, rel_x))

                display.blit(pygame.transform.rotate(rocket, angle), (self.x, self.y))
                self.hitbox = pygame.Rect(self.x, self.y, 8, 8)
        if self.exploding:
            display.blit(explosion, (self.x, self.y))
            self.exploding_timer -= 1

            if self.exploding_timer <= 0:
                self.exploding = False

        self.death_radius = pygame.Rect(self.x - 50, self.y - 50, 100, 100)
        self.damage_radius = pygame.Rect(self.x - 100, self.y - 100, 200, 200)

    def explode(self, mode):
        """ (Rocket, str) -> None
            Kill/damage all enemies/players in the respective radius. Enemy rockets will not kill other enemies (mode
            is either "Enemy" or "Player", and is which character fired the rocket. However, the player can still be
            damaged by their own rocket.
        """
        # 1. Damage enemies
        for enemy in enemies:
            if mode != "Enemy":
                if pygame.Rect.colliderect(enemy.hitbox, self.death_radius):
                    if enemy.health != 0:
                        enemy.health = 0
                        try:  # Will result in error for dogs
                            if enemy.primary_weapon == ithaca37:  # Different weapons mean harder enemies, so the player
                                player.money += 100  # gets more money
                            elif enemy.primary_weapon == m3:
                                player.money += 125
                            elif enemy.primary_weapon == springfield:
                                player.money += 150
                            elif enemy.primary_weapon == bazooka:
                                player.money += 200
                            elif enemy.primary_weapon == m1carbine:
                                player.money += 275
                            elif enemy.primary_weapon == tank_turret:
                                player.money += 500
                        except AttributeError:
                            player.money += 150
                        player.hitmarker_chain = FPS
                        player.kills += 1

                elif pygame.Rect.colliderect(enemy.hitbox, self.damage_radius):
                    if enemy.health != 0:
                        enemy.health -= 95
                        player.hitmarker_chain = FPS

                        if enemy.health <= 0 and not enemy.dead:
                            try:  # Will result in error for dogs
                                if enemy.primary_weapon == ithaca37:
                                    player.money += 100
                                elif enemy.primary_weapon == m3:
                                    player.money += 125
                                elif enemy.primary_weapon == springfield:
                                    player.money += 150
                                elif enemy.primary_weapon == bazooka:
                                    player.money += 200
                                elif enemy.primary_weapon == m1carbine:
                                    player.money += 275
                                elif enemy.primary_weapon == tank_turret:
                                    player.money += 500
                            except AttributeError:
                                player.money += 150
                            player.kills += 1

        # 2. Damage the player
        if pygame.Rect.colliderect(player.hitbox, self.death_radius):
            player.health = 0
        elif pygame.Rect.colliderect(player.hitbox, self.damage_radius):
            player.health -= 95

        if sound_fx:
            if not self.exploding:
                pygame.mixer.Channel(4).play(explosion_sound)

        self.exploding = True


class Grenade(Rocket):
    def __init__(self, x, y, mouse_x, mouse_y, gun, damage):
        """ (Grenade, int, int, int, int, Gun, int) -> None
            Gun parameter isn't really needed, but is for class inheritance. Grenades are thrown by the player, and
            they bounce around for 5 seconds before exploding. The distance traveled per frame decreases over time.
            Since they explode the same way a rocket does, we use class inheritance
        """
        super().__init__(x, y, mouse_x, mouse_y, gun, damage)
        self.type = "Grenade"
        self.range = 5 * FPS

        self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - display_scroll[1], 50, 50)

        self.x_vel = math.cos(self.angle) * 4
        self.y_vel = math.sin(self.angle) * 4

        self.speed_modifier = 2

    def main(self):
        """ (Grenade) -> None
            Main function of the grenade. It calculates if the grenade would bounce if it moved, and if it would, then
            bounce it instead.
        """
        global objects

        bounce = False

        self.range -= 1
        if self.range == 0:
            self.explode("Player")
        elif self.range > 0:
            # Check if there would be a collision if it moved on its current path
            tentative_hitbox = pygame.Rect(self.x - int(self.x_vel), self.y - int(self.y_vel), 50, 50)
            for object in objects:
                if pygame.Rect.colliderect(tentative_hitbox, object.hitbox):
                    if not object.pass_through:
                        self.x_vel = -self.x_vel  # Reverse the directions of the grenade
                        self.y_vel = -self.y_vel
                        bounce = True

            if not bounce:
                self.x -= int(self.x_vel * self.speed_modifier)
                self.y -= int(self.y_vel * self.speed_modifier)

                self.speed_modifier *= 0.99

            rel_x, rel_y = self.x - int(self.x_vel) - self.x, self.y - int(self.y_vel) - self.y
            angle = -((180 / math.pi) * math.atan2(rel_y, rel_x))

            display.blit(pygame.transform.rotate(grenade, angle), (self.x, self.y))

        self.death_radius = pygame.Rect(self.x - 50, self.y - 50, 100, 100)
        self.damage_radius = pygame.Rect(self.x - 100, self.y - 100, 200, 200)

        self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - display_scroll[1], 50, 50)


class C4:
    def __init__(self, x, y):
        """ (C4, int, int) -> None
            Create the C4 object. C4 is a remote-controlled explosive, so the player can put it down and blow it up
            later.
        """
        self.x = x
        self.y = y

        self.death_radius = pygame.Rect(self.x - 50 - display_scroll[0], self.y - 50 - display_scroll[1], 100, 100)
        self.damage_radius = pygame.Rect(self.x - 100 - display_scroll[0], self.y - 100 - display_scroll[1], 200, 200)

        self.exploding = False
        self.explosion_countdown = round(FPS)

    def main(self):
        """ (C4) -> None
            Draw the C4 onto the screen. If it is exploding, it will draw an explosion for a second before removing
            itself.
        """
        if self.exploding:
            if self.explosion_countdown > 0:
                display.blit(explosion, (self.x - display_scroll[0], self.y - display_scroll[1]))
                self.explosion_countdown -= 1

            else:
                list_of_c4.remove(self)
        else:
            display.blit(pygame.image.load(r"weapons\c4.png"), (self.x - display_scroll[0], self.y - display_scroll[1]))

        self.death_radius = pygame.Rect(self.x - 50 - display_scroll[0], self.y - 50 - display_scroll[1], 100, 100)
        self.damage_radius = pygame.Rect(self.x - 100 - display_scroll[0], self.y - 100 - display_scroll[1], 200, 200)

    def explode(self):
        """ (C4) -> None
            Blow up the C4. Since enemies can't use C4, I don't have to account for that.
        """
        for enemy in enemies:
            if pygame.Rect.colliderect(enemy.hitbox, self.death_radius):
                if not enemy.dead:
                    try:  # Will result in error for dogs
                        if enemy.primary_weapon == ithaca37:
                            player.money += 100
                        elif enemy.primary_weapon == m3:
                            player.money += 125
                        elif enemy.primary_weapon == springfield:
                            player.money += 150
                        elif enemy.primary_weapon == bazooka:
                            player.money += 200
                        elif enemy.primary_weapon == m1carbine:
                            player.money += 275
                        elif enemy.primary_weapon == tank_turret:
                            player.money += 500
                    except AttributeError:
                        player.money += 150
                    player.hitmarker_chain = FPS
                    enemy.health = 0
                    player.kills += 1
                    enemy.dead = True
            elif pygame.Rect.colliderect(enemy.hitbox, self.damage_radius):
                enemy.health -= 95
                if not enemy.dead:
                    if enemy.health <= 0:
                        try:  # Will result in error for dogs
                            if enemy.primary_weapon == ithaca37:
                                player.money += 100
                            elif enemy.primary_weapon == m3:
                                player.money += 125
                            elif enemy.primary_weapon == springfield:
                                player.money += 150
                            elif enemy.primary_weapon == bazooka:
                                player.money += 200
                            elif enemy.primary_weapon == m1carbine:
                                player.money += 275
                            elif enemy.primary_weapon == tank_turret:
                                player.money += 500
                        except AttributeError:
                            player.money += 150
                        enemy.dead = True
                        player.kills += 1
                        player.hitmarker_chain = FPS
        if pygame.Rect.colliderect(player.hitbox, self.death_radius):
            player.health = 0
        elif pygame.Rect.colliderect(player.hitbox, self.damage_radius):
            player.health -= 95

        self.exploding = True
        if sound_fx:
            pygame.mixer.Channel(4).play(explosion_sound)


class American:
    def __init__(self, x, y, primary_weapon, secondary_weapon, health):
        """ (American, int, int, Gun, Gun, int) -> None
            Create the American object, the enemies in this game. They have a simple AI where they will attempt to
            reach a point within 50 pixels of the player, but not actually on the player. If they hit a solid object,
            their pathfinding will automatically change
        """
        self.x = x
        self.y = y
        # Slightly modify the American's starting position so they don't all spawn on top of each other
        self.x += randint(-50, 50)
        self.y += randint(-50, 50)

        self.animation_count = 0
        self.reset_offset = 0
        self.offset_x = randrange(-500, 500)
        self.offset_y = randrange(-500, 500)

        self.primary_weapon = primary_weapon
        self.secondary_weapon = secondary_weapon

        self.health = health

        self.target_x, self.target_y = player.x + randrange(-50, 50), player.y + randrange(-50, 50)

        self.fire_delay = round(self.primary_weapon.fire_delay * FPS / randint(8, 12))  # Delay between shots fired
        self.hitbox = pygame.Rect(self.x, self.y, 30, 45)
        self.dead = False
        self.angle = None
        self.type = "Human"
        self.sub_type = "Normal"

    def handle_weapons(self):
        """ (American) --> None
            Display the weapon, pointed towards the player.
        """
        rel_x, rel_y = player.x + display_scroll[0] - self.x, player.y + display_scroll[1] - self.y
        self.angle = -((180 / math.pi) * math.atan2(rel_y, rel_x))

        display.blit(pygame.transform.rotate(self.primary_weapon.image, self.angle),
                     (self.x + self.primary_weapon.x_offset - int(
                         self.primary_weapon.image.get_width() / 2 + display_scroll[0]),
                      self.y + self.primary_weapon.y_offset - int(self.primary_weapon.image.get_height() / 2) -
                      display_scroll[1]))

    def handle_weapon_dead(self):
        """ (American) -> None
            Draws the gun on screen if the enemy is dead
        """
        display.blit(pygame.transform.rotate(self.primary_weapon.image, self.angle),
                     (self.x - display_scroll[0], self.y - display_scroll[1]))

    def shoot(self):
        """ (American) -> None
            Creates a bullet that flies out toward the player, with a small margin of error (30 pixels)
        """
        enemy_bullets.append(Bullet(self.x - display_scroll[0], self.y + 22 - display_scroll[1],
                                    player.x + randrange(-30, 30), player.y + randrange(-30, 30),
                                    self.primary_weapon, self.primary_weapon.damage))
        if sound_fx:
            if not pygame.mixer.Channel(1).get_busy():
                pygame.mixer.Channel(1).play(enemy_gunfire)

    def main(self):
        """ (American) -> None
            Draws the enemy onto the screen, and moves it towards the player. Dead enemies are drawn flipped over
        """
        if self.sub_type == "Normal":
            enemy_walk_images = american_walk_images
        else:
            enemy_walk_images = sniper_images

        if self.health <= 0:
            display.blit(pygame.transform.rotate(pygame.transform.scale(enemy_walk_images[0], (32, 42)), 270),
                         (self.x - display_scroll[0], self.y - display_scroll[1]))
            self.dead = True
            self.handle_weapon_dead()
        else:
            self.handle_weapons()

            if self.animation_count > 14:
                self.animation_count = 0
            else:
                self.animation_count += 1

            if self.reset_offset == 0:  # If it is time to find a new target location to move towards
                self.offset_x = randrange(-500, 500)
                self.offset_y = randrange(-500, 500)
                self.reset_offset = randrange(120, 150)  # Frames left until a new target location is chosen again
            else:
                self.reset_offset -= 1

            # Check for collisions
            collision = False
            if player.y + self.offset_y > self.y - display_scroll[1] and player.x + self.offset_x > self.x - \
                    display_scroll[0]:
                self.hitbox = pygame.Rect(self.x + 1 - display_scroll[0], self.y + 1 - display_scroll[1], 32,
                                          42)
                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.y += 1
                    self.x += 1
                    if self.x - display_scroll[0] > player.x:
                        display.blit(pygame.transform.scale(
                            pygame.transform.flip(enemy_walk_images[self.animation_count // 4], True, False),
                            (32, 42)),
                            (self.x - display_scroll[0], self.y - display_scroll[1]))
                    else:
                        display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                     (self.x - display_scroll[0], self.y - display_scroll[1]))
                if collision:
                    display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
                    self.offset_x = randrange(-500, 500)
                    self.offset_y = randrange(-500, 500)
                    self.reset_offset = randrange(120, 150)
            elif player.y + self.offset_y > self.y - display_scroll[1] and player.x + self.offset_x < self.x - \
                    display_scroll[0]:
                self.hitbox = pygame.Rect(self.x - 1 - display_scroll[0], self.y + 1 - display_scroll[1], 32,
                                          42)
                for object in objects:
                    if not object.pass_through:
                        if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                            collision = True
                        else:
                            collision = False
                if not collision:
                    self.y += 1
                    self.x -= 1
                    if self.x - display_scroll[0] > player.x:
                        display.blit(pygame.transform.scale(
                            pygame.transform.flip(enemy_walk_images[self.animation_count // 4], True, False),
                            (32, 42)),
                            (self.x - display_scroll[0], self.y - display_scroll[1]))
                    else:
                        display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                     (self.x - display_scroll[0], self.y - display_scroll[1]))
                if collision:
                    display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
                    self.offset_x = randrange(-500, 500)
                    self.offset_y = randrange(-500, 500)
                    self.reset_offset = randrange(120, 150)
            elif player.y + self.offset_y < self.y - display_scroll[1] and player.x + self.offset_x > self.x - \
                    display_scroll[0]:
                self.hitbox = pygame.Rect(self.x + 1 - display_scroll[0], self.y - 1 - display_scroll[1], 32,
                                          42)
                for object in objects:
                    if not object.pass_through:
                        if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                            collision = True
                        else:
                            collision = False
                if not collision:
                    self.y -= 1
                    self.x += 1
                    if self.x - display_scroll[0] > player.x:
                        display.blit(pygame.transform.scale(
                            pygame.transform.flip(enemy_walk_images[self.animation_count // 4], True, False),
                            (32, 42)),
                            (self.x - display_scroll[0], self.y - display_scroll[1]))
                    else:
                        display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                     (self.x - display_scroll[0], self.y - display_scroll[1]))
                if collision:
                    display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
                    self.offset_x = randrange(-500, 500)
                    self.offset_y = randrange(-500, 500)
                    self.reset_offset = randrange(120, 150)
            elif player.y + self.offset_y < self.y - display_scroll[1] and player.x + self.offset_x < self.x - \
                    display_scroll[0]:
                self.hitbox = pygame.Rect(self.x - 1 - display_scroll[0], self.y - 1 - display_scroll[1], 32,
                                          42)
                for object in objects:
                    if not object.pass_through:
                        if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                            collision = True
                        else:
                            collision = False
                if not collision:
                    self.y -= 1
                    self.x -= 1
                    if self.x - display_scroll[0] > player.x:
                        display.blit(pygame.transform.scale(
                            pygame.transform.flip(enemy_walk_images[self.animation_count // 4], True, False),
                            (32, 42)),
                            (self.x - display_scroll[0], self.y - display_scroll[1]))
                    else:
                        display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                     (self.x - display_scroll[0], self.y - display_scroll[1]))
                if collision:
                    display.blit(pygame.transform.scale(enemy_walk_images[self.animation_count // 4], (32, 42)),
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
                    self.offset_x = randrange(-500, 500)
                    self.offset_y = randrange(-500, 500)
                    self.reset_offset = randrange(120, 150)
            else:
                if self.x - display_scroll[0] > player.x:
                    display.blit(pygame.transform.scale(
                        pygame.transform.flip(enemy_walk_images[0], True, False), (32, 42)),
                        (self.x - display_scroll[0], self.y - display_scroll[1]))
                else:
                    display.blit(pygame.transform.scale(enemy_walk_images[0], (32, 42)),
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))

            # Shoot, if the fire delay has elapsed
            self.fire_delay -= 1
            if self.fire_delay <= 0:
                self.fire_delay = round(self.primary_weapon.fire_delay * FPS / randint(8, 12))
                self.shoot()

            self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - display_scroll[1], 30, 45)


class Dog:
    def __init__(self, x, y, health):
        """ (Dog, int, int, int) -> None
            Create the Dog object. In-game, attack dogs move toward the player and kill them if they collide
        """
        self.x = x
        self.y = y

        self.animation_count = 0
        self.target_x, self.target_y = player.x, player.y
        self.hitbox = pygame.Rect(self.x, self.y, 39, 21)
        self.health = 100
        self.dead = False
        self.type = "Dog"
        self.health = health

    def main(self):
        """ (Dog) -> None
            Move towards the player
        """
        if self.health <= 0:
            display.blit(pygame.transform.rotate(dog_images[0], 270),
                         (self.x - display_scroll[0], self.y - display_scroll[1]))
            self.dead = True
        else:
            if self.animation_count + 1 >= 16:
                self.animation_count = 0

            self.animation_count += 1

            collision = False

            if player.y > self.y - display_scroll[1] and player.x > self.x - display_scroll[0]:
                self.hitbox = pygame.Rect(self.x + 2 - display_scroll[0], self.y + 2 - display_scroll[1], 39,
                                          21)
                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.y += 2
                    self.x += 2
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_down = True
                    self.can_move_right = True
                if collision:
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_down = False
                    self.can_move_right = False
            elif player.y > self.y - display_scroll[1] and player.x < self.x - display_scroll[0]:
                self.hitbox = pygame.Rect(self.x - 2 - display_scroll[0], self.y + 2 - display_scroll[1], 39,
                                          21)
                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.y += 2
                    self.x -= 2
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        if self.x - display_scroll[0] < player.x:
                            display.blit(
                                pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                                (self.x - display_scroll[0],
                                 self.y - display_scroll[1]))
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_down = True
                    self.can_move_left = True
                if collision:
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        if self.x - display_scroll[0] < player.x:
                            display.blit(
                                pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                                (self.x - display_scroll[0],
                                 self.y - display_scroll[1]))
                    self.can_move_down = False
                    self.can_move_left = False
            elif player.y < self.y - display_scroll[1] and player.x > self.x - display_scroll[0]:
                self.hitbox = pygame.Rect(self.x + 2 - display_scroll[0], self.y - 2 - display_scroll[1], 39,
                                          21)
                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.y -= 2
                    self.x += 2
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))

                    self.can_move_up = True
                    self.can_move_right = True
                if collision:
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_up = False
                    self.can_move_right = False
            elif player.y < self.y - display_scroll[1] and player.x < self.x - display_scroll[0]:
                self.hitbox = pygame.Rect(self.x - 2 - display_scroll[0], self.y - 2 - display_scroll[1], 39,
                                          21)
                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.y -= 2
                    self.x -= 2
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_up = True
                    self.can_move_left = True
                if collision:
                    self.y -= 2
                    self.x -= 2
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_up = False
                    self.can_move_left = False
            elif player.y > self.y - display_scroll[1]:
                self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y + 2 - display_scroll[1], 39, 21)

                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.y += 2

                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_down = True
                if collision:
                    self.can_move_down = False
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
            elif player.y < self.y - display_scroll[1]:
                self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - 2 - display_scroll[1], 39, 21)

                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.y -= 2

                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_up = True
                if collision:
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_up = False
            elif player.x < self.x - display_scroll[0]:
                self.hitbox = pygame.Rect(self.x - 2 - display_scroll[0], self.y - display_scroll[1], 39, 21)

                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.x -= 2

                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_left = True
                if collision:
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_left = False
            elif player.x > self.x - display_scroll[0]:
                self.hitbox = pygame.Rect(self.x + 2 - display_scroll[0], self.y - display_scroll[1], 39, 21)

                for object in objects:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False

                if not collision:
                    self.x += 2

                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_right = True
                if collision:
                    if self.x - display_scroll[0] < player.x:
                        display.blit(
                            pygame.transform.flip(dog_images[self.animation_count // 4], True, False),
                            (self.x - display_scroll[0],
                             self.y - display_scroll[1]))
                    else:
                        display.blit(dog_images[self.animation_count // 4], (self.x - display_scroll[0],
                                                                             self.y - display_scroll[1]))
                    self.can_move_right = False

            self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - display_scroll[1], 39, 21)


class Sniper(American):
    def __init__(self, x, y, primary_weapon, secondary_weapon, health):
        """ (Sniper, int, int, Gun, Gun, int) -> None
            Create the Sniper object, a child class of the American object. The only difference is that it has a
            different skin.
        """
        super().__init__(x, y, primary_weapon, secondary_weapon, health)
        self.sub_type = "Sniper"


class Grenadier(American):
    def __init__(self, x, y, primary_weapon, secondary_weapon, health):
        """ (Grenadier, int, int, Gun, Gun, int) -> None
            Create the Grenadier object, a child of the American class. Grenadiers are armed with rocket launchers, so
            when they shoot, they shoot a rocket instead of a bullet
        """
        super().__init__(x, y, primary_weapon, secondary_weapon, health)

    def shoot(self):
        """ (Grenadier) -> None
            Shoots a rocket instead of a bullet
        """
        enemy_bullets.append(
            Rocket(self.x - display_scroll[0], self.y + 22 - display_scroll[1], player.x + randrange(-30, 30),
                   player.y + randrange(-30, 30), self.primary_weapon, self.primary_weapon.damage))
        if sound_fx:
            pygame.mixer.Channel(6).play(rocket_launch)


class Tank(Grenadier):
    def __init__(self, x, y, primary_weapon, secondary_weapon, health):
        """ (Tank, int, int, Gun, Gun, int) -> None
            Tanks are enemies with a ton of health and shoot rockets. It is a child of the Grenadier class, since they
            are actually very similar
        """
        super().__init__(x, y, primary_weapon, secondary_weapon, health)

        self.type = "Tank"
        self.health *= 20  # Tanks have 20x the health of normal enemies from the same wave.

    def main(self):
        """ (Tank) -> None
            Make the tank move around towards the player
        """
        if self.reset_offset == 0:
            self.offset_x = randrange(-500, 500)
            self.offset_y = randrange(-500, 500)
            self.reset_offset = randrange(120, 150)
        else:
            self.reset_offset -= 1

        collision = False
        if player.y + self.offset_y > self.y - display_scroll[1] and player.x + self.offset_x > self.x - \
                display_scroll[0]:
            self.hitbox = pygame.Rect(self.x + 1 - display_scroll[0], self.y + 1 - display_scroll[1], 200,
                                      104)
            for object in objects:
                if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                    collision = True
                else:
                    collision = False

            if not collision:
                self.y += 1
                self.x += 1
                if self.x - display_scroll[0] > player.x:
                    display.blit(
                        pygame.transform.flip(tank_images[0], True, False),
                        (self.x - display_scroll[0], self.y - display_scroll[1]))
                else:
                    display.blit(tank_images[0],
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
            if collision:
                display.blit(tank_images[0],
                             (self.x - display_scroll[0], self.y - display_scroll[1]))
                self.offset_x = randrange(-500, 500)
                self.offset_y = randrange(-500, 500)
                self.reset_offset = randrange(120, 150)
        elif player.y + self.offset_y > self.y - display_scroll[1] and player.x + self.offset_x < self.x - \
                display_scroll[0]:
            self.hitbox = pygame.Rect(self.x - 1 - display_scroll[0], self.y + 1 - display_scroll[1], 200,
                                      104)
            for object in objects:
                if not object.pass_through:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False
            if not collision:
                self.y += 1
                self.x -= 1
                if self.x - display_scroll[0] > player.x:
                    display.blit(
                        pygame.transform.flip(tank_images[0], True, False),
                        (self.x - display_scroll[0], self.y - display_scroll[1]))
                else:
                    display.blit(tank_images[0],
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
            if collision:
                display.blit(tank_images[0],
                             (self.x - display_scroll[0], self.y - display_scroll[1]))
                self.offset_x = randrange(-500, 500)
                self.offset_y = randrange(-500, 500)
                self.reset_offset = randrange(120, 150)
        elif player.y + self.offset_y < self.y - display_scroll[1] and player.x + self.offset_x > self.x - \
                display_scroll[0]:
            self.hitbox = pygame.Rect(self.x + 1 - display_scroll[0], self.y - 1 - display_scroll[1], 200,
                                      104)
            for object in objects:
                if not object.pass_through:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False
            if not collision:
                self.y -= 1
                self.x += 1
                if self.x - display_scroll[0] > player.x:
                    display.blit(
                        pygame.transform.flip(tank_images[0], True, False),
                        (self.x - display_scroll[0], self.y - display_scroll[1]))
                else:
                    display.blit(tank_images[0],
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
            if collision:
                display.blit(tank_images[0],
                             (self.x - display_scroll[0], self.y - display_scroll[1]))
                self.offset_x = randrange(-500, 500)
                self.offset_y = randrange(-500, 500)
                self.reset_offset = randrange(120, 150)
        elif player.y + self.offset_y < self.y - display_scroll[1] and player.x + self.offset_x < self.x - \
                display_scroll[0]:
            self.hitbox = pygame.Rect(self.x - 1 - display_scroll[0], self.y - 1 - display_scroll[1], 200,
                                      104)
            for object in objects:
                if not object.pass_through:
                    if pygame.Rect.colliderect(self.hitbox, object.hitbox):
                        collision = True
                    else:
                        collision = False
            if not collision:
                self.y -= 1
                self.x -= 1
                if self.x - display_scroll[0] > player.x:
                    display.blit(
                        pygame.transform.flip(tank_images[0], True, False),
                        (self.x - display_scroll[0], self.y - display_scroll[1]))
                else:
                    display.blit(tank_images[0],
                                 (self.x - display_scroll[0], self.y - display_scroll[1]))
            if collision:
                display.blit(tank_images[0],
                             (self.x - display_scroll[0], self.y - display_scroll[1]))
                self.offset_x = randrange(-500, 500)
                self.offset_y = randrange(-500, 500)
                self.reset_offset = randrange(120, 150)
        else:
            if self.x - display_scroll[0] > player.x:
                display.blit(
                    pygame.transform.flip(tank_images[0], True, False),
                    (self.x - display_scroll[0], self.y - display_scroll[1]))
            else:
                display.blit(tank_images[0],
                             (self.x - display_scroll[0], self.y - display_scroll[1]))

        self.fire_delay -= 1
        if self.fire_delay <= 0:
            self.fire_delay = round(self.primary_weapon.fire_delay * FPS / randint(8, 12))
            self.shoot()

        self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - display_scroll[1], 200, 104)

        self.handle_weapons()


class Object:
    def __init__(self, position, image_string, colorkey, width, height, pass_through):
        """ (Object, int, int, str, tuple, int, int, boolean) -> None
            Create the Object object. These are obstacles on screen, to provide scenery and cover. Some objects, like
            trees, can be shot and walk through, while others, like rocks, are solid
        """
        self.x = position[0]
        self.y = position[1]
        self.image = pygame.image.load(image_string).convert()
        self.image.set_colorkey(colorkey)
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(self.x, self.y, width, height)
        self.pass_through = pass_through

    def main(self):
        """ (Object) -> None
            Draw the object onto the screen.
        """
        self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - display_scroll[1], self.width, self.height)
        display.blit(pygame.transform.scale(self.image, (self.width, self.height)),
                     (self.x - display_scroll[0], self.y - display_scroll[1]))


class WeaponArmoury(Object):
    def __init__(self, position, image_string, colorkey, width, height, pass_through):
        """ (WeaponArmoury, int, int, str, tuple, int, int, boolean) -> None
            The weapon armoury is a special Object where the player can buy items throughout the game.
        """
        super().__init__(position, image_string, colorkey, width, height, pass_through)
        self.access_rect = pygame.Rect(self.x - 50 - display_scroll[0], self.y - 50 - display_scroll[1],
                                       self.width + 100, self.height + 100)
        self.accessing_weapon_armory = False
        self.access_menu = "Main Weapon Armory"

    def main(self):
        """ (WeaponArmoury) -> None
            Draws the weapon armoury onto the screen. If the player is accessing the armoury, it will display all the
            buy options on the screen
        """
        self.hitbox = pygame.Rect(self.x - display_scroll[0], self.y - display_scroll[1], self.width,
                                  self.height)
        display.blit(self.image, (self.x - display_scroll[0], self.y - display_scroll[1]))
        self.access_rect = pygame.Rect(self.x - 50 - display_scroll[0], self.y - 50 - display_scroll[1],
                                       self.width + 100, self.height + 100)
        # access_rect is the area the player must be in to be able to buy access the store

        if self.accessing_weapon_armory:
            if self.access_menu == "Main Weapon Armory":
                display.blit(pygame.image.load(r"options/weapon_armory_title.png").convert(), (600, 195))
                if player.money >= 750:
                    display.blit(pygame.image.load(r"options/refill.png").convert(), (600, 245))
                else:
                    display.blit(pygame.image.load(r"options/refill_cant_afford.png").convert(), (600, 245))
                display.blit(pygame.image.load(r"options/pistols.png").convert(), (600, 265))
                display.blit(pygame.image.load(r"options/shotguns.png").convert(), (600, 285))
                display.blit(pygame.image.load(r"options/snipers.png").convert(), (600, 305))
                display.blit(pygame.image.load(r"options/submachineguns.png").convert(), (600, 325))
                display.blit(pygame.image.load(r"options/assaultrifles.png").convert(), (600, 345))
                display.blit(pygame.image.load(r"options/lightmachineguns.png").convert(), (600, 365))
                display.blit(pygame.image.load(r"options/launchers.png").convert(), (600, 385))
                if player.money >= 1000:
                    display.blit(pygame.image.load(r"options/grenade_refill.png").convert(), (600, 405))
                else:
                    display.blit(pygame.image.load(r"options/grenade_refill_cant_afford.png").convert(), (600, 405))
                if player.money >= 3000:
                    display.blit(pygame.image.load(r"options/c4.png").convert(), (600, 425))
                else:
                    display.blit(pygame.image.load(r"options/c4_cant_afford.png").convert(), (600, 425))
                if player.money >= 2000:
                    display.blit(pygame.image.load(r"options/armour.png").convert(), (600, 445))
                else:
                    display.blit(pygame.image.load(r"options/armour_cant_afford.png").convert(), (600, 445))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 465))
            if self.access_menu == "Pistols":
                display.blit(pygame.image.load(r"options/pistols_title.png").convert(), (600, 195))
                if player.money >= 250:
                    display.blit(pygame.image.load(r"options/mauserc96.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/colt.png").convert(), (600, 265))
                else:
                    display.blit(pygame.image.load(r"options/mauserc96_cant_afford.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/colt_cant_afford.png").convert(), (600, 265))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 285))
            if self.access_menu == "Shotguns":
                display.blit(pygame.image.load(r"options/shotguns_title.png").convert(), (600, 195))
                if player.money >= 2000:
                    display.blit(pygame.image.load(r"options/ithaca37.png").convert(), (600, 245))
                else:
                    display.blit(pygame.image.load(r"options/ithaca37_cant_afford.png").convert(), (600, 245))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 265))
            if self.access_menu == "Snipers":
                display.blit(pygame.image.load(r"options/snipers_title.png").convert(), (600, 195))
                if player.money >= 2000:
                    display.blit(pygame.image.load(r"options/springfield.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/mosin_nagant.png").convert(), (600, 265))
                else:
                    display.blit(pygame.image.load(r"options/springfield_cant_afford.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/mosin_nagant_cant_afford.png").convert(), (600, 265))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 285))
            if self.access_menu == "SMGs":
                display.blit(pygame.image.load(r"options/submachineguns_title.png").convert(), (600, 195))
                if player.money >= 2000:
                    display.blit(pygame.image.load(r"options/m3.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/type50.png").convert(), (600, 265))
                else:
                    display.blit(pygame.image.load(r"options/m3_cant_afford.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/type50_cant_afford.png").convert(), (600, 265))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 285))
            if self.access_menu == "Assault Rifles":
                display.blit(pygame.image.load(r"options/assaultrifles_title.png").convert(), (600, 195))
                if player.money >= 3000:
                    display.blit(pygame.image.load(r"options/m1carbine.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/sks.png").convert(), (600, 265))
                else:
                    display.blit(pygame.image.load(r"options/m1carbine_cant_afford.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/sks_cant_afford.png").convert(), (600, 265))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 285))
            if self.access_menu == "LMGs":
                display.blit(pygame.image.load(r"options/lightmachineguns_title.png").convert(), (600, 195))
                if player.money >= 7000:
                    display.blit(pygame.image.load(r"options/bren.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/dp27.png").convert(), (600, 265))
                else:
                    display.blit(pygame.image.load(r"options/bren_cant_afford.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/dp27_cant_afford.png").convert(), (600, 265))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 285))
            if self.access_menu == "Launchers":
                display.blit(pygame.image.load(r"options/launchers_title.png").convert(), (600, 195))
                if player.money >= 7000:
                    display.blit(pygame.image.load(r"options/bazooka.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/rpg7.png").convert(), (600, 265))
                else:
                    display.blit(pygame.image.load(r"options/bazooka_cant_afford.png").convert(), (600, 245))
                    display.blit(pygame.image.load(r"options/rpg7_cant_afford.png").convert(), (600, 265))
                display.blit(pygame.image.load(r"options/back.png").convert(), (600, 285))

    def access(self):
        """ (WeaponArmoury) -> None
            Opens up the access menu
        """
        self.accessing_weapon_armory = True
        self.access_menu = "Main Weapon Armory"


def show_campaign_hud():
    """ (None) -> None
        Shows the HUD when playing in campaign mode. It's the same as Survival mode, but without the Survival
        mechanics. I also got rid of campaign mode, so I don't really have a need for this function anymore.
    """
    current_weapon = bigger_hud_font.render(player.primary_weapon.name, True, (0, 0, 0))
    display.blit(current_weapon, (10, 950))

    secondary_weapon = hud_font.render(player.secondary_weapon.name, True, (0, 0, 0))
    display.blit(secondary_weapon, (10, 1000))

    magazine_ammo = hud_font.render(
        (str(player.primary_weapon.magazine_ammo) + " | " + str(player.primary_weapon.reserve_ammo)), True, (0, 0, 0))
    display.blit(magazine_ammo, (10, 925))

    health = hud_font.render(("Health: " + str(player.health)), True, (0, 0, 0))
    display.blit(health, (1775, 1050))

    grenades = hud_font.render("Grenades: " + str(player.grenades), True, (0, 0, 0))
    display.blit(grenades, (1775, 1000))

    c4 = hud_font.render("C4: " + str(player.c4_inventory), True, (0, 0, 0))
    display.blit(c4, (1775, 975))

    if player.primary_weapon.reloading:
        reloading_text = hud_font.render(
            "Reloading . . . " + str(round(player.primary_weapon.frames_remaining / 60, 1)), True, BLACK)
        display.blit(reloading_text, (80, 925))


def show_survival_hud(wave, live_enemies):
    """ (None) -> None
    Shows the HUD for the player in Survival mode
    """
    current_weapon = bigger_hud_font.render(player.primary_weapon.name, True, (0, 0, 0))
    display.blit(current_weapon, (10, 950))

    secondary_weapon = hud_font.render(player.secondary_weapon.name, True, (0, 0, 0))
    display.blit(secondary_weapon, (10, 1000))

    magazine_ammo = hud_font.render(
        (str(player.primary_weapon.magazine_ammo) + " | " + str(player.primary_weapon.reserve_ammo)), True, (0, 0, 0))
    display.blit(magazine_ammo, (10, 925))

    wave_text = hud_font.render(("Wave: " + str(wave)), True, (0, 0, 0))
    display.blit(wave_text, (10, 10))

    health = hud_font.render(("Health: " + str(player.health)), True, (0, 0, 0))
    display.blit(health, (1775, 1050))

    armour = hud_font.render(("Body Armour: " + str(player.armour)), True, (0, 0, 0))
    display.blit(armour, (1775, 1025))

    money = hud_font.render(("Money: $" + str(player.money)), True, (0, 0, 0))
    display.blit(money, (10, 900))

    enemies_left = hud_font.render(("Enemies Left: " + str(len(live_enemies))), True, (0, 0, 0))
    display.blit(enemies_left, (10, 25))

    grenades = hud_font.render("Grenades: " + str(player.grenades), True, (0, 0, 0))
    display.blit(grenades, (1775, 1000))

    c4 = hud_font.render("C4: " + str(player.c4_inventory), True, (0, 0, 0))
    display.blit(c4, (1775, 975))

    if player.primary_weapon.reloading:
        reloading_text = hud_font.render(
            "Reloading . . . " + str(round(player.primary_weapon.frames_remaining / 60, 1)), True, BLACK)
        display.blit(reloading_text, (80, 925))


def random_game_area(player_hitbox):
    """ (None) -> Tuple
        Returns a tuple of two random values of the playable game area for spawning objects, and makes sure that they
        don't generate on top of the player
    """
    while True:
        seed = randint(-1920, 1920 * 2), randint(-1020, 1020 * 2)
        generated_rect = pygame.Rect(seed[0] - display_scroll[0] - 100, seed[1] - display_scroll[1] - 100, 200, 200)
        if pygame.Rect.colliderect(generated_rect, player_hitbox):
            continue
        else:
            break

    return seed


# Create all the pre-determined objects on screen
display_scroll = [100, 100]  # This determines the offset of everything onscreen so the player looks like they're moving
weapon_armory = WeaponArmoury((500, 40), "objects/weaponarmory.png", (71, 112, 76), 100, 88, False)
weapon_armory_icon = Object((510, 25), "weapons/sks.png", (71, 112, 76), 64, 11, True)
survival_sam_launcher = Object((400, 500), "objects/sam.png", (71, 112, 76), 150, 99, False)
boot_camp_npc = Object((800, 500), r"animations\player\player_walk_0.png", WHITE, 32, 42, False)

player_bullets = []  # List of projectiles shot by the player
enemy_bullets = []  # List of projectiles shot by the enemies

grenades = []  # List of grenades thrown by the player
player = Player(720, 450, 32, 32, mauserc96, m1911)  # Create the player object
objects = []
list_of_c4 = []

paused = False


def game_engine(objects, game_mode, wave, message=None):
    """ (List, str, int, str) -> str
        This function is executed every frame. All the game's mechanics happen here. A string is returned that says
        the status of what happened during that frame.
    """
    # 1. Global variables needed
    global enemies
    global paused

    # 2. Background of screen
    display.fill(GREEN)

    # 3. Check for events
    mouse_x, mouse_y = pygame.mouse.get_pos()
    for event in pygame.event.get():
        # 3.1. Exit game
        if event.type == pygame.QUIT:
            exit()
            pygame.quit()
        # 3.2 Shoot
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if player.primary_weapon.magazine_ammo == 0:
                    pass  # The player can't shoot if there is no ammo in their weapon
                else:
                    if not player.primary_weapon.reloading:
                        if (player.primary_weapon.name == "M20 Super Bazooka") or (
                                "RPG-7" in player.primary_weapon.name):  # Fire a rocket instead
                            player_bullets.append(
                                Rocket(player.x, player.y + 22, mouse_x, mouse_y, player.primary_weapon,
                                       player.primary_weapon.damage))
                            if sound_fx:
                                pygame.mixer.Channel(3).play(rocket_launch)
                        else:  # Otherwise, shoot a regular bullet
                            player_bullets.append(
                                Bullet(player.x, player.y + 22, mouse_x, mouse_y, player.primary_weapon,
                                       player.primary_weapon.damage))
                            if sound_fx:
                                pygame.mixer.Channel(0).play(gunfire)
                        player.primary_weapon.magazine_ammo -= 1  # Take away one bullet

        if event.type == pygame.MOUSEBUTTONUP:
            # 3.3. Reset the fire delay for automatic weapons
            if player.primary_weapon.fire_mode == "automatic":
                player.primary_weapon.fire_delay_ticker = player.primary_weapon.fire_delay

            # 3.4. Detect if the player has purchased something from the armory
            if pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Player clicked the refill bullet ammo option
                if player.money >= 750:
                    player.money -= 750
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            if pygame.Rect.colliderect(pygame.Rect(600, 405, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Player clicked the refill grenades ammo option
                if player.money >= 1000:
                    player.money -= 1000
                    player.grenades = 4
            if pygame.Rect.colliderect(pygame.Rect(600, 425, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Player clicked the refill c4 option
                if player.money >= 3000:
                    player.money -= 3000
                    player.c4_inventory = 10
            if pygame.Rect.colliderect(pygame.Rect(600, 445, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Player clicked the refill c4 option
                if player.money >= 2000:
                    player.money -= 2000
                    player.armour = 200
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Pistols
                weapon_armory.access_menu = "Pistols"
            elif pygame.Rect.colliderect(pygame.Rect(600, 285, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Shotguns
                weapon_armory.access_menu = "Shotguns"
            elif pygame.Rect.colliderect(pygame.Rect(600, 305, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Snipers
                weapon_armory.access_menu = "Snipers"
            elif pygame.Rect.colliderect(pygame.Rect(600, 325, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Submachine Guns
                weapon_armory.access_menu = "SMGs"
            elif pygame.Rect.colliderect(pygame.Rect(600, 345, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Assault Rifles
                weapon_armory.access_menu = "Assault Rifles"
            elif pygame.Rect.colliderect(pygame.Rect(600, 365, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Light Machine Guns
                weapon_armory.access_menu = "LMGs"
            elif pygame.Rect.colliderect(pygame.Rect(600, 385, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Launchers
                weapon_armory.access_menu = "Launchers"
            elif pygame.Rect.colliderect(pygame.Rect(600, 465, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Main Weapon Armory":  # Escape option
                weapon_armory.accessing_weapon_armory = False
            elif pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Pistols":  # Buy Mauser C96
                if player.money >= 250:
                    player.money -= 250
                    player.primary_weapon = mauserc96
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Pistols":  # Buy Colt M1911
                if player.money >= 250:
                    player.money -= 250
                    player.primary_weapon = m1911
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 285, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Pistols":  # Leave
                weapon_armory.accessing_weapon_armory = False
            elif pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Shotguns":  # Buy Ithaca 37
                if player.money >= 2000:
                    player.money -= 2000
                    player.primary_weapon = ithaca37
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Shotguns":  # Leave
                weapon_armory.accessing_weapon_armory = False
            elif pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Snipers":  # Buy Springfield
                if player.money >= 2000:
                    player.money -= 2000
                    player.primary_weapon = springfield
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Snipers":  # Buy Mosin Nagant
                if player.money >= 2000:
                    player.money -= 2000
                    player.primary_weapon = mosin_nagant
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 285, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Snipers":  # Leave
                weapon_armory.accessing_weapon_armory = False
            elif pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "SMGs":  # Buy M3
                if player.money >= 2000:
                    player.money -= 2000
                    player.primary_weapon = m3
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "SMGs":  # Buy PPsh-41 Type 50
                if player.money >= 2000:
                    player.money -= 2000
                    player.primary_weapon = type50
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 285, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "SMGs":  # Leave
                weapon_armory.accessing_weapon_armory = False
            elif pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Assault Rifles":  # Buy M1 Carbine
                if player.money >= 3000:
                    player.money -= 3000
                    player.primary_weapon = m1carbine
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Assault Rifles":  # Buy SKS
                if player.money >= 3000:
                    player.money -= 3000
                    player.primary_weapon = sks
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 285, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Assault Rifles":  # Leave
                weapon_armory.accessing_weapon_armory = False
            elif pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "LMGs":  # Buy Bren
                if player.money >= 7000:
                    player.money -= 7000
                    player.primary_weapon = bren
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "LMGs":  # Buy DP-27 Type 53
                if player.money >= 7000:
                    player.money -= 7000
                    player.primary_weapon = dp27
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 285, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "LMGs":  # Leave
                weapon_armory.accessing_weapon_armory = False
            elif pygame.Rect.colliderect(pygame.Rect(600, 245, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Launchers":  # Buy Bazooka
                if player.money >= 7000:
                    player.money -= 7000
                    player.primary_weapon = bazooka
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 265, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Launchers":  # Buy RPG-7
                if player.money >= 7000:
                    player.money -= 7000
                    player.primary_weapon = rpg7
                    player.primary_weapon.magazine_ammo = player.primary_weapon.magazine_capacity
                    player.primary_weapon.reserve_ammo = player.primary_weapon.reserve_capacity
                    player.secondary_weapon.magazine_ammo = player.secondary_weapon.magazine_capacity
                    player.secondary_weapon.reserve_ammo = player.secondary_weapon.reserve_capacity
            elif pygame.Rect.colliderect(pygame.Rect(600, 285, 240, 20), pygame.Rect(mouse_x, mouse_y, 1, 1)) \
                    and weapon_armory.accessing_weapon_armory and weapon_armory.access_menu == "Launchers":  # Leave
                weapon_armory.accessing_weapon_armory = False

        if event.type == pygame.KEYDOWN:  # Check for key presses. These keys are for those that are only meant to be
            key = pygame.key.get_pressed()  # pressed once, as otherwise, the game thinks you are holding these keys

            # Leave the menu
            if key[pygame.K_ESCAPE] and game_mode == "Survival" and weapon_armory.accessing_weapon_armory:
                weapon_armory.accessing_weapon_armory = False

            #  Swap weapon
            if key[pygame.K_1] or key[pygame.K_2]:
                player.swap_weapon()

            #  Reload
            if key[pygame.K_r]:
                if player.primary_weapon.magazine_ammo < player.primary_weapon.magazine_capacity:
                    player.primary_weapon.reload()

            # Throw grenade
            if key[pygame.K_g]:
                if player.grenades > 0:
                    if player.grenade_cooldown == 0:
                        player.throw_grenade()
                        player.grenades -= 1

            # Place C4
            if key[pygame.K_n]:
                if player.c4_inventory > 0:
                    if player.c4_cooldown == 0:
                        list_of_c4.append(C4(player.x + display_scroll[0], player.y + display_scroll[1]))
                        player.c4_inventory -= 1

                        player.c4_cooldown = FPS * 2

            # Detonate C4
            if key[pygame.K_j]:
                for explosive in list_of_c4:
                    explosive.explode()

            # If the player can swap weapons with a dead enemy
            for enemy in enemies:
                if enemy.dead:
                    try:
                        if enemy.x - display_scroll[0] - 50 <= player.x <= enemy.x - display_scroll[
                            0] + 50 and enemy.y - display_scroll[1] - 50 <= player.y <= enemy.y - display_scroll[
                            1] + 50:
                            if key[pygame.K_f]:
                                player_current_weapon = player.primary_weapon
                                enemy_current_weapon = enemy.primary_weapon

                                player.primary_weapon = enemy_current_weapon
                                enemy.primary_weapon = player_current_weapon
                    except AttributeError:
                        pass  # If  the player walks over a dead attack dog

            # Pause game
            if key[pygame.K_h]:
                if paused:
                    paused = False
                else:
                    paused = True

    if not paused:
        # 4. Movement
        key = pygame.key.get_pressed()
        can_move_left = True
        can_move_right = True
        can_move_up = True
        can_move_down = True
        if key[pygame.K_a]:
            for object in objects:
                player_would_be_hitbox = pygame.Rect(player.x - 5, player.y, 27, 42)
                if not object.pass_through:
                    if pygame.Rect.colliderect(object.hitbox, player_would_be_hitbox):
                        can_move_left = False
                        break
        if key[pygame.K_d]:
            for object in objects:
                player_would_be_hitbox = pygame.Rect(player.x + 5, player.y, 27, 42)
                if not object.pass_through:
                    if pygame.Rect.colliderect(object.hitbox, player_would_be_hitbox):
                        can_move_right = False
                        break
        if key[pygame.K_w]:
            for object in objects:
                player_would_be_hitbox = pygame.Rect(player.x, player.y - 5, 27, 42)
                if not object.pass_through:
                    if pygame.Rect.colliderect(object.hitbox, player_would_be_hitbox):
                        can_move_up = False
                        break
        if key[pygame.K_s]:
            for object in objects:
                player_would_be_hitbox = pygame.Rect(player.x, player.y + 5, 27, 42)
                if not object.pass_through:
                    if pygame.Rect.colliderect(object.hitbox, player_would_be_hitbox):
                        can_move_down = False
                        break

        if key[pygame.K_a] and can_move_left:
            display_scroll[0] -= 5
            player.moving_right = False
            player.moving_left = True
            for bullet in player_bullets:
                bullet.x += 5
            for grenade in grenades:
                grenade.x += 5
            for bullet in enemy_bullets:
                bullet.x += 5

        if key[pygame.K_d] and can_move_right:
            display_scroll[0] += 5
            player.moving_left = False
            player.moving_right = True
            for bullet in player_bullets:
                bullet.x -= 5
            for grenade in grenades:
                grenade.x -= 5
            for bullet in enemy_bullets:
                bullet.x -= 5
        if key[pygame.K_w] and can_move_up:
            display_scroll[1] -= 5
            for bullet in player_bullets:
                bullet.y += 5
            for grenade in grenades:
                grenade.y += 5
            for bullet in enemy_bullets:
                bullet.y += 5

        if key[pygame.K_s] and can_move_down:
            display_scroll[1] += 5
            for bullet in player_bullets:
                bullet.y -= 5
            for grenade in grenades:
                grenade.y -= 5
            for bullet in enemy_bullets:
                bullet.y -= 5

        # 5. Shooting automatic weapons
        if pygame.mouse.get_pressed()[0]:
            if not player.primary_weapon.reloading:
                if player.primary_weapon.fire_mode == "automatic":
                    player.primary_weapon.fire_delay_ticker -= 1
                    if player.primary_weapon.fire_delay_ticker == 0:
                        player.primary_weapon.fire_delay_ticker = player.primary_weapon.fire_delay
                    if player.primary_weapon.fire_delay_ticker == player.primary_weapon.fire_delay:
                        if player.primary_weapon.magazine_ammo == 0:
                            pass
                        else:
                            player_bullets.append(
                                Bullet(player.x, player.y + 22, mouse_x, mouse_y, player.primary_weapon,
                                       player.primary_weapon.damage))
                            if sound_fx:
                                pygame.mixer.Channel(0).play(gunfire)
                            player.primary_weapon.magazine_ammo -= 1

        # 6. Display text for weapon swapping
        for enemy in enemies:
            if enemy.dead:
                try:
                    if enemy.x - display_scroll[0] - 50 <= player.x <= enemy.x - display_scroll[0] + 50 and enemy.y - \
                            display_scroll[1] - 50 <= player.y <= enemy.y - display_scroll[1] + 50:
                        swap_weapon = hud_font.render("Press F to swap for " + enemy.primary_weapon.name, True,
                                                      (0, 0, 0))
                        display.blit(swap_weapon, (720, 495))
                except AttributeError:
                    pass  # If  the player walks over a dead attack dog

        # 7. Call the main function for all the objects

        player.primary_weapon.main()

        for explosive in list_of_c4:
            explosive.main()

        if player.health <= 0:
            return "Dead"
        else:
            player.main()

        for object in objects:
            if not object.pass_through:
                object.main()
        for enemy in enemies:
            enemy.main()

        for bullet in player_bullets:
            bullet.main()

        for bullet in enemy_bullets:
            bullet.main()

        for grenade in grenades:
            grenade.main()

        if game_mode == "Survival":
            weapon_armory.main()

        #  Hit detection for bullets
        for bullet in player_bullets:
            if bullet.range < 0:  # If the bullet's range has been reached:
                if bullet.type != "Rocket":
                    player_bullets.remove(bullet)
                else:
                    if bullet.exploding_timer < 1:
                        player_bullets.remove(bullet)
                    else:
                        bullet.explode("Normal")

            else:
                if bullet.type == "Bullet":
                    for enemy in enemies:
                        if not enemy.dead:
                            if pygame.Rect.colliderect(
                                    pygame.Rect(enemy.hitbox[0], enemy.hitbox[1], enemy.hitbox[2], enemy.hitbox[3]),
                                    bullet.hitbox):
                                try:
                                    player_bullets.remove(bullet)
                                except ValueError:  # For some reason this causes errors, so I included a try statement
                                    pass
                                enemy.health -= bullet.damage
                                if enemy.health <= 0:
                                    try:  # Will result in error for dogs
                                        if enemy.primary_weapon == ithaca37:
                                            player.money += 100
                                        elif enemy.primary_weapon == m3:
                                            player.money += 125
                                        elif enemy.primary_weapon == springfield:
                                            player.money += 150
                                        elif enemy.primary_weapon == bazooka:
                                            player.money += 200
                                        elif enemy.primary_weapon == m1carbine:
                                            player.money += 275
                                        elif enemy.primary_weapon == tank_turret:
                                            player.money += 500
                                    except AttributeError:
                                        player.money += 150
                                    player.kills += 1
                                    player.hitmarker_chain = FPS
                                else:
                                    player.hitmarker_chain = FPS
                                    if sound_fx:
                                        pygame.mixer.Channel(2).play(hitmarker_sound)

                    for object in objects:
                        if not object.pass_through:
                            if object.hitbox[0] - display_scroll[0] <= bullet.x - display_scroll[0] <= object.hitbox[
                                0] + \
                                    object.hitbox[2] - display_scroll[0] and object.hitbox[1] - display_scroll[
                                1] <= bullet.y - \
                                    display_scroll[1] <= object.hitbox[1] + object.hitbox[3] - display_scroll[1]:
                                try:
                                    player_bullets.remove(bullet)
                                except ValueError:  # For some reason this causes errors, so I included a try statement
                                    pass
                elif bullet.type == "Rocket":
                    for enemy in enemies:
                        if not enemy.dead:
                            if pygame.Rect.colliderect(
                                    pygame.Rect(enemy.hitbox[0], enemy.hitbox[1], enemy.hitbox[2], enemy.hitbox[3]),
                                    bullet.hitbox):
                                enemy.health -= bullet.damage
                                try:
                                    bullet.explode("Normal")
                                except ValueError:  # For some reason this causes errors, so I included a try statement
                                    pass
                    for object in objects:
                        if object.pass_through == False:
                            if object.hitbox[0] - display_scroll[0] <= bullet.x - display_scroll[0] <= object.hitbox[
                                0] + \
                                    object.hitbox[2] - display_scroll[0] and object.hitbox[1] - display_scroll[
                                1] <= bullet.y - \
                                    display_scroll[1] <= object.hitbox[1] + object.hitbox[3] - display_scroll[1]:
                                try:
                                    bullet.explode("Normal")
                                except ValueError:  # For some reason this causes errors, so I included a try statement
                                    pass

        for bullet in enemy_bullets:
            if bullet.range < 0:  # If the bullet's range has been reached:
                if bullet.type != "Rocket":
                    enemy_bullets.remove(bullet)
                if bullet.type == "Rocket":
                    if bullet.exploding_timer < 1:
                        enemy_bullets.remove(bullet)
                    else:
                        bullet.explode("Enemy")
            if bullet.type == "Bullet":
                if player.hitbox[0] - display_scroll[0] <= bullet.x - display_scroll[0] <= player.hitbox[
                    0] + player.hitbox[
                    2] - display_scroll[0] and player.hitbox[1] - display_scroll[1] <= bullet.y - display_scroll[
                    1] <= \
                        player.hitbox[1] + player.hitbox[3] - display_scroll[1]:
                    player.health -= bullet.damage
                    try:
                        enemy_bullets.remove(bullet)
                    except ValueError:  # For some reason this sometimes causes errors, so I included a try statement
                        pass
                for object in objects:
                    if not object.pass_through:
                        if object.hitbox[0] - display_scroll[0] <= bullet.x - display_scroll[0] <= object.hitbox[0] + \
                                object.hitbox[2] - display_scroll[0] and object.hitbox[1] - display_scroll[
                            1] <= bullet.y - \
                                display_scroll[1] <= object.hitbox[1] + object.hitbox[3] - display_scroll[1]:
                            try:
                                enemy_bullets.remove(bullet)
                            except ValueError:  # For some reason this causes errors, so I included a try statement
                                pass
            elif bullet.type == "Rocket":
                if player.hitbox[0] - display_scroll[0] <= bullet.x - display_scroll[0] <= player.hitbox[
                    0] + player.hitbox[
                    2] - display_scroll[0] and player.hitbox[1] - display_scroll[1] <= bullet.y - display_scroll[
                    1] <= \
                        player.hitbox[1] + player.hitbox[3] - display_scroll[1]:
                    if bullet.exploding_timer < 1:
                        enemy_bullets.remove(bullet)
                    else:
                        bullet.explode("Enemy")
                    try:
                        pass
                    except ValueError:  # For some reason this sometimes causes errors, so I included a try statement
                        pass
                for object in objects:
                    if not object.pass_through:
                        if object.hitbox[0] - display_scroll[0] <= bullet.x - display_scroll[0] <= object.hitbox[0] + \
                                object.hitbox[2] - display_scroll[0] and object.hitbox[1] - display_scroll[
                            1] <= bullet.y - \
                                display_scroll[1] <= object.hitbox[1] + object.hitbox[3] - display_scroll[1]:
                            try:
                                if bullet.exploding_timer < 1:
                                    enemy_bullets.remove(bullet)
                                else:
                                    bullet.explode("Enemy")
                            except ValueError:  # For some reason this causes errors, so I included a try statement
                                pass

        # Remove dead tanks and put a solid object in their place
        for enemy in enemies:
            if enemy.type == "Tank" and enemy.health <= 0:
                objects.append(
                    Object((enemy.x, enemy.y), r"animations\enemy\tank\tank.png", (0, 0, 0), 200, 104, False))
                enemies.remove(enemy)

        # If player can access armories
        if pygame.Rect.colliderect(weapon_armory.access_rect, player.hitbox):
            access_weapon_armory = hud_font.render("Press F to access weapon armory", True, BLACK)
            display.blit(access_weapon_armory, (720, 495))
            if key[pygame.K_f]:
                weapon_armory.access()
        else:
            weapon_armory.accessing_weapon_armory = False

        for enemy in enemies:
            if not enemy.dead and enemy.type == "Dog":
                if pygame.Rect.colliderect(pygame.Rect(enemy.hitbox), pygame.Rect(player.hitbox)):
                    player.health -= 100

        # Check collision against tanks
        for enemy in enemies:
            if enemy.type == "Tank":
                if pygame.Rect.colliderect(enemy.hitbox, player.hitbox):
                    player.health = 0

        for object in objects:
            if object.pass_through:
                object.main()

        # Draw hitmarkers
        if player.hitmarker_chain > 0:
            display.blit(hitmarker, (mouse_x - 16, mouse_y - 16))

        live_enemies = []
        for enemy in enemies:
            if not enemy.dead:
                live_enemies.append(enemy)

        if game_mode == "Campaign":
            show_campaign_hud()
        elif game_mode == "Survival":
            show_survival_hud(wave, live_enemies)
            if message is not None:
                text_y = 800
                for line in message:
                    display.blit(hud_font.render(line, True, BLACK), (700, text_y))
                    text_y += 15

        if len(live_enemies) == 0:
            return "Next Wave"
    else:
        pass


def campaign():
    """ (None) -> None
        Campaign game mode, which I never actually used.
    """
    global enemies
    objects = []
    enemies = [Tank(500, 500, tank_turret, m1911, 100), Grenadier(500, 500, bazooka, m1911, 100)]

    while True:
        game_status = game_engine(objects, "Campaign", None)
        if game_status == "Dead":
            break

        clock.tick(FPS)
        pygame.display.update()  # Update the game

    death_screen()


def tutorial():
    """ (None) -> None
        Text-only tutorial mode that I got rid of later."
    """
    tutorial_text = [
        'Mission Briefing',
        '',
        'The enemy is launching an all-out attack on our only surface-to-air missile site in the area. If it is ',
        "destroyed, enemy air support will be able to fly past and turn the war in the enemy's favour. Reinforcements are",
        'on their way, but you are on your own for now',
        '',
        'You have two pistols. Use them to kill enemies and earn money. If you run out of ammunition, you can',
        'pick up enemy weapons from the ground. The first few waves of enemies are armed with shotguns. They have very ',
        'little range, but are dangerous up close. As the attack continues, the enemies will have better weapons and more',
        'health. They eventually switch to M3 Submachine Guns, which do less damage but shoot faster and further. Lastly,',
        'they switch to M1 Carbines, which do more damage and have an even further range.',
        '',
        'You will also encounter many special enemies. Some will be armed with rocket launchers that shoot explosive ',
        'rockets at you. These will explode upon impact on objects, or after a certain amount of time. Being nearby will',
        'instantly kill you, or heavily damage you. Enemies armed with sniper rifles also appear. They have camouflage,',
        'and although they shoot slowly, they can shoot you from beyond your vision and do a lot of damage. Attack Dogs',
        "can also appear. These dogs will run straight at you, and if they get to you, you're dead. Lastly, enemy tanks",
        'will begin arriving. They can only be destroyed with our anti-tank RPGs, or enemy Bazookas you may find, so ',
        'prepare yourself beforehand.',
        '',
        'Use your equipment to your benefit. You have 10 packs of C4. Use these to set traps and detonate them remotely.',
        'You also have four grenades. Use them on large groups of enemies for best effect. You also have body armour. ',
        'This will protect you from taking damage at first, but it will eventually wear off.  To stay alive, buy more ',
        'equipment from the Weapons Armoury. You can replenish your grenades, C4 and body armour supply, refill your ',
        'ammunition, or buy better guns. Spend your money wisely, as it will get tight. ',
        '',
        'In combat, use the money rocks around the area for cover to hide from bullets. Bullets can not pass through, but',
        'enemies can climb over them to reach you. Good luck. HQ out.',
        '',
        'Controls:',
        'Move: W - Up, A - Left, S - Down, D - Right',
        'Shoot: Left Mouse',
        'Reload: R',
        'Throw Grenade: G',
        'Switch Weapon: 1 / 2',
        'Pick Up Weapon / Access Weapon Armoury: F',
        'Pause Game: ESC',
        'Deploy C4: N',
        'Detonate C4: J',
        '',
        'Return to Main Menu: ESC']

    reading = True

    while reading:
        display.fill(WHITE)
        text_y = 10
        for line in tutorial_text:
            display.blit(hud_font.render(line, True, BLACK), (0, text_y))
            text_y += 15

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            reading = False

        clock.tick(FPS)
        pygame.display.update()

    start_menu()


def survival():
    """ (None) -> None
        The Survival game mode.
    """
    global enemies
    global live_enemies
    global objects
    global display_scroll
    # Survival game mode. Hold off endless waves of enemies that get progressively harder. Get money for kills and
    # challenges, and use it to buy equipment, guns and ammo.
    wave = 0
    enemies = []
    live_enemies = []
    objects = [weapon_armory, weapon_armory_icon, survival_sam_launcher]

    player.health = 100
    player.in_tutorial = False
    player.armour = 200
    player.primary_weapon = mauserc96
    player.secondary_weapon = m1911
    player.hitmarker_chain = 0
    player.money = 0
    player.kills = 0
    display_scroll = [100, 100]

    if music:
        pygame.mixer.Channel(5).play(game_music, -1)
        pygame.mixer.Channel(5).set_volume(0.7)

    for i in range(1, 100):
        objects.append(Object(random_game_area(player.hitbox), "objects/tree1.png", (71, 112, 76), 106, 128, True))
        objects.append(Object(random_game_area(player.hitbox), "objects/rock1.png", BLACK, 100, 91, False))

    while True:
        if wave == 1:
            game_status = game_engine(objects, "Survival", wave, message=[
                'The enemy is launching an all-out attack on our only surface-to-air missile site in the area. If it is ',
                "destroyed, enemy air support will be able to fly past and turn the war in the enemy's favour. Reinforcements are",
                'on their way, but you are on your own for now.', ])
        else:
            game_status = game_engine(objects, "Survival", wave)
        if game_status == "Dead":
            break
        elif game_status == "Next Wave":
            wave += 1
            if wave == 1:
                for i in range(1, 6):
                    enemies.append(American(0, 0, ithaca37, m1911,
                                            100 + (wave - 1) * 10))  # Plus 10 HP for every round after round 1
                    enemies.append(
                        American(3000, 3000, ithaca37, m1911, 100 + (wave - 1) * 10))
                live_enemies = enemies
            elif wave == 2:
                for i in range(1, 5):
                    enemies.append(American(0, 0, ithaca37, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(0, 2000, ithaca37, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 0, ithaca37, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 2000, ithaca37, m1911, 100 + (wave - 1) * 10))
                live_enemies = enemies
            elif wave == 3:
                for i in range(1, 6):
                    enemies.append(
                        American(randrange(-50, 50), randrange(-50, 50), ithaca37, m1911, 100 + (wave - 1) * 10))
                    enemies.append(
                        American(randrange(2950, 3050), randrange(1950, 2050), ithaca37, m1911, 100 + (wave - 1) * 10))
                enemies.append(Dog(0, 0, 50 + (wave - 1) * 10))
                enemies.append(Dog(3000, 3000, 50 + (wave - 1) * 10))
                live_enemies = enemies
            elif wave == 4:
                for i in range(1, 6):
                    enemies.append(American(randrange(-50, 50), randrange(-50, 50), m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(
                        American(randrange(2950, 3050), randrange(1950, 2050), m3, m1911, 100 + (wave - 1) * 10))
                live_enemies = enemies
            elif wave == 5:
                for i in range(1, 4):
                    enemies.append(American(0, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(0, 2000, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 2000, m3, m1911, 100 + (wave - 1) * 10))
                live_enemies = enemies
            elif wave == 6:
                enemies.append(Sniper(0, 0, springfield, m1911, 100 + (wave - 1) * 10))
                enemies.append(Sniper(0, 2000, springfield, m1911, 100 + (wave - 1) * 10))
                live_enemies = enemies
            elif wave == 7:
                for i in range(1, 4):
                    enemies.append(American(0, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(0, 2000, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 2000, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(2000, 2000, m3, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(0, 0, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(2000, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(3000, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
            elif wave == 8:
                for i in range(1, 4):
                    enemies.append(American(0, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(0, 2000, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 2000, m3, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(0, 0, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(0, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(3000, 0, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(3000, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
            elif wave == 9:
                for i in range(1, 4):
                    enemies.append(American(0, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(0, 2000, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 0, m3, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 2000, m3, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(0, 0, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(0, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(3000, 0, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(3000, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(-1000, -1000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Dog(0, 0, 50 + (wave - 1) * 10))
                enemies.append(Dog(3000, 3000, 50 + (wave - 1) * 10))
            elif wave == 10:
                enemies.append(Tank(0, 0, tank_turret, tank_turret, 100 + (wave - 1) * 10))
            else:
                for i in range(1, 4):
                    enemies.append(American(0, 0, m1carbine, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(0, 2000, m1carbine, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 0, m1carbine, m1911, 100 + (wave - 1) * 10))
                    enemies.append(American(3000, 2000, m1carbine, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(0, 0, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(0, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(3000, 0, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(3000, 2000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Grenadier(-1000, -1000, bazooka, m1911, 100 + (wave - 1) * 10))
                enemies.append(Dog(0, 0, 50 + (wave - 1) * 10))
                enemies.append(Dog(3000, 3000, 50 + (wave - 1) * 10))
                enemies.append(Tank(0, 0, tank_turret, tank_turret, 100 + (wave - 1) * 10))
                enemies.append(Sniper(0, 0, springfield, m1911, 100 + (wave - 1) * 10))
                enemies.append(Sniper(0, 2000, springfield, m1911, 100 + (wave - 1) * 10))

        clock.tick(FPS)
        pygame.display.update()  # Update the game

    death_screen(wave, player.kills)


def bootcamp():
    """ (None) -> None
        An interactive tutorial for the player. Each wave, the player will be introduced to a new important feature
        in the game. Only one enemy will come each time, so the player will have plenty of time to understand.
    """
    global enemies
    global live_enemies
    global objects
    global display_scroll

    wave = 0
    enemies = []
    live_enemies = []
    objects = [boot_camp_npc, weapon_armory, weapon_armory_icon]

    if music:
        pygame.mixer.Channel(5).play(game_music, -1)
        pygame.mixer.Channel(5).set_volume(0.7)

    player.in_tutorial = False
    player.primary_weapon = mauserc96
    player.secondary_weapon = m1911
    player.hitmarker_chain = 0
    player.kills = 0
    display_scroll = [100, 100]

    player.money = 100000
    player.health = 1000
    player.armour = 0

    player.in_tutorial = True

    for i in range(1, 100):
        objects.append(Object(random_game_area(player.hitbox), "objects/tree1.png", (71, 112, 76), 106, 128, True))
        objects.append(Object(random_game_area(player.hitbox), "objects/rock1.png", BLACK, 100, 91, False))

    message = [""]

    while True:
        game_status = game_engine(objects, "Survival", wave, message)
        if game_status == "Dead":
            break
        elif game_status == "Next Wave":
            wave += 1
            if wave == 1:
                # Shooting tutorial
                message = [
                    "Welcome to boot camp. I'm Colonel Tang, and I'm going to be your instructor for today. Firstly, ",
                    "you need to learn how to shoot. Left click to shoot your weapon. Once you've figured that out, a ",
                    " target will come. Shoot it down."
                ]
                enemies.append(American(2000, 2000, m1911, m1911, 100))
            if wave == 2:
                # Movement tutorial
                message = [
                    "Good job. Now in case you haven't figured it out, here's how to move. W for up, A for left, S ",
                    "for down and D for right. Now take down another target. You might want to reload first by ",
                    "pressing R. This allows you to choose when to put more ammo into your weapon. Fun fact: if you ",
                    "reload a gun with zero bullets loaded, it reloads slower than a gun with some bullets still ",
                    "inside. That's because there is already a bullet in the chamber, so you don't have to manually ",
                    "insert one."
                ]
                enemies.append(American(2000, 2000, m1911, m1911, 100))
            if wave == 3:
                # Refill ammo tutorial
                message = [
                    "Great. Now, you might be running low on ammo. Head to the weapon armoury and press F to open it. ",
                    "Buy an ammo refill to get all the ammunition you can carry. Note that it refills your secondary, ",
                    "too. That reminds me, you can hold two weapons at a time. Press 1 or 2 to switch between them. ",
                    "Remember, switching to your secondary is always faster than reloading. Anyways, take down one ",
                    "more target.",
                    "",
                    "Here's a tip: you can hide from bullets by taking cover on the other side of a solid object, ",
                    "like a rock. It will stop bullets, but not the enemy. They can climb over them, or crawl ",
                    "underneath. But that won't work for you, since you're carrying a lot more stuff."
                ]
                enemies.append(American(2000, 2000, m1911, m1911, 100))
            if wave == 4:
                # Enemy shotgun tutorial
                message = [
                    "The targets so far have been armed with pistols. But the Americans are going to be better ",
                    "equipped than that. This next target will be armed with a shotgun. Shotguns have a very tiny ",
                    "range, but they do a ton of damage if they hit you. Avoid getting too close to them. "
                ]
                enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 5:
                # Using a shotgun tutorial
                message = [
                    "In case you ever have to use one, you need to know how to use a shotgun effectively. Take cover ",
                    "behind a solid object, a shoot an enemy when they get close by peeking out of cover. Buy a ",
                    "shotgun from the weapon armoury, or pick one up from the previous target by walking over and ",
                    "pressing F."
                ]
                enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 6:
                # Enemy SMG tutorial
                message = [
                    "Some other enemies could be armed with submachine guns. These have about the same range of a ",
                    "pistol, but shoot fast and do a bit more damage. When fighting against enemies with SMGs, try ",
                    "to keep out of their range, and don't get surrounded. "
                ]
                enemies.append(American(2000, 2000, m3, m1911, 100))
            if wave == 7:
                # Using a SMG tutorial
                message = [
                    "SMGs are also useful weapons to use. They are automatic, which means you can hold down the ",
                    "trigger to keep shooting. Buy or pick up an SMG and use it to take down the next target."
                ]
                enemies.append(American(2000, 2000, m3, m1911, 100))
            if wave == 8:
                # Health regen tutorial
                message = [
                    "By now, you've probably been hit a couple of times. However, your health will automatically heal ",
                    "over time. This time, allow yourself to be hit by the target a few times, before taking it down. ",
                    "Pay close attention to your health indicator and see how it heals."
                ]
                enemies.append(American(2000, 2000, m3, m1911, 100))
            if wave == 9:
                # Enemy assault rifle tutorial
                message = [
                    "Assault rifles are another type of weapon you'll see enemies using. These fire more slowly than ",
                    "SMGs, but do more damage. They also have more range, so stay behind cover and don't make yourself",
                    " more vulnerable than you have to."
                ]
                enemies.append(American(2000, 2000, m1carbine, m1911, 100))
            if wave == 10:
                # Using an assault rifle tutorial
                message = [
                    "Assault rifles are semi-automatic, which means one pull of the trigger only shoots one bullet. ",
                    "Since they are more powerful, you might want to try using one. Use an assault rifle to take down ",
                    "this next target."
                ]
                enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 11:
                # Enemy sniper tutorial
                message = [
                    "You'll probably encounter enemy snipers. They usually camouflage themselves, so be alert. They ",
                    "have sniper rifles and shoot slowly, but they can shoot you from an extreme distance and still ",
                    "hit. Stay behind cover until after they shoot, because they'll be vulnerable for a moment as ",
                    "they pull the bolt for another shot."
                ]
                enemies.append(Sniper(2000, 2000, springfield, m1911, 100))
            if wave == 12:
                # Using a sniper tutorial
                message = [
                    "Sniper rifles are also useful weapons themselves. Since they have a long range, you can take out ",
                    "enemies from a distance before they can hit you. However, you might want to stick around next to ",
                    "the weapon armoury, because they can't hold much ammo and they have to reload often."
                ]
                enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 13:
                # Using an LMG tutorial
                message = [
                    "Now you won't find any enemies using a light machine gun, but we have them here in the armory. ",
                    "These guns have a huge amount of ammunition, but they don't do a lot of damage or have much ",
                    "range. But their large firepower makes up for it. These are great for mowing down groups of ",
                    "enemies clumped together, as you don't need to reload. LMGs are also fully automatic. But they ",
                    "have a long reload time, so watch your ammo. Buy an LMG and take out those targets."
                ]
                for _ in range(5):
                    enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 14:
                # Enemy rocket launcher tutorial
                message = [
                    "You're also going to encounter enemies with rocket launchers. Rockets are dangerous, and if one ",
                    "explodes too close to you, you're dead and there's nothing you can do about it. They will ",
                    "explode once they run out of range, or as soon as they collide with another solid object. ",
                    "Rockets travel more slowly, though, and are loud, so get moving as soon as you notice one ",
                    "coming for you."
                ]
                enemies.append(Grenadier(2000, 2000, bazooka, m1911, 100))
            if wave == 15:
                # Using a rocket launcher tutorial
                message = [
                    "You can use rocket launchers as well. They are good for taking out large groups of enemies, ",
                    "and are the only way to reliably destroy tanks, which we'll get to later. Remember not to ",
                    "hit a rock in front of you and blow yourself up though. "
                ]
                for _ in range(5):
                    enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 16:
                # Enemy attack dog tutorial
                message = [
                    "The enemy will be using attack dogs. These guys are fast, and if they get a hold of you, you're ",
                    "dead. Kill them before they reach you, or they'll knock you to the ground. Try these targets. "
                ]
                enemies.append(Dog(2000, 2000, 50))
                enemies.append(Dog(2000, 2000, 50))
            if wave == 17:
                # Enemy tank tutorial
                message = [
                    "The last enemy type you might find is the tank. Tanks shoot explosive torpedoes at you, so be ",
                    "careful. You could damage them with bullets, but that'll take thousands of bullets. Instead, ",
                    "the best option is to use explosives. I hope you still have the rocket launcher, because now ",
                    "a tank target is headed towards you. "
                ]
                enemies.append(Tank(2000, 1500, tank_turret, m1911, 1000))
            if wave == 18:
                # Grenade tutorial
                message = [
                    "Good job. Rockets aren't the only explosive - your vest allows you to hold up to four frag ",
                    "grenades at a time. Press G to throw a grenade. They'll explode after five seconds. They also ",
                    "bounce back if they collide with a solid object, so be wary of that. Use grenades to take out ",
                    "this next enemy."
                ]
                enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 19:
                # C4 tutorial
                message = [
                    "You also have access to C4. Press N to deploy C4 on the area you're standing on. Then, retreat ",
                    "to a safe distance and press J to detonate them. You can use C4 to set traps - place them down, ",
                    "and blow them up manually once the enemy walks over them. Try taking out this next target using ",
                    "C4. "
                ]
                enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 20:
                # Refill tutorial
                message = [
                    "Alright, that's all you need to know. Go back to the weapon armoury and refill all the equipment ",
                    "you've used. Buy some body armour as well - it will absorb damage so it won't damage you ",
                    "instead. ",
                    "",
                    "You're going to be tasked with defending a surface-to-air missile site near the front lines. ",
                    "It's about a two miles trek, so as soon as you take out this last target, get walking. ",
                    "The rest of your squadron will catch up soon, but for a while, you'll have the entire site to ",
                    "yourself.",
                ]
                enemies.append(American(2000, 2000, ithaca37, m1911, 100))
            if wave == 21:
                start_menu()

        clock.tick(FPS)
        pygame.display.update()  # Update the game

    death_screen(wave, player.kills)


def death_screen(wave=None, kills=None):
    """ (None) -> None
        The death screen displayed at the end of the game.
    """
    game_over = hud_font.render("YOU DIED", True, RED)
    display.blit(game_over, (900, 300))

    if wave is not None:
        wave_text = hud_font.render("You made it to wave " + str(wave) + ".", True, BLACK)
        display.blit(wave_text, (900, 350))
        kills_text = hud_font.render("You got " + str(kills) + " kills.", True, BLACK)
        display.blit(kills_text, (900, 365))

    quote = small_hud_font.render(choice(death_quotes), True, (0, 0, 0))
    quote_rect = quote.get_rect()
    display.blit(quote, (960 - quote_rect[2] / 2, 400))

    leave_text = small_hud_font.render("Press ESC to return to the main menu.", True, (0, 0, 0))
    leave_text_rect = leave_text.get_rect()
    display.blit(leave_text, (960 - leave_text_rect[2] / 2, 420))

    if music:
        pygame.mixer.Channel(5).play(defeat_music)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        key = pygame.key.get_pressed()
        if key[pygame.K_ESCAPE]:
            start_menu()

        clock.tick(FPS)
        pygame.display.update()


def settings():
    """ (None) -> None
        Allow the player the control the settings
    """
    global music
    global sound_fx

    if music:
        pygame.mixer.Channel(5).play(menu_music, -1)

    while True:
        display.fill(GREEN)
        if music:
            if sound_fx:
                display.blit(settings_on_on, (0, 0))
            else:
                display.blit(settings_on_off, (0, 0))
        else:
            if sound_fx:
                display.blit(settings_off_on, (0, 0))
            else:
                display.blit(settings_off_off, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_rect = pygame.Rect(mouse_x, mouse_y, 1, 1)
                if pygame.Rect.colliderect(mouse_rect, pygame.Rect(150, 214, 197, 49)):
                    if music:
                        music = False
                        pygame.mixer.Channel(5).set_volume(0)
                    else:
                        music = True
                        pygame.mixer.Channel(5).set_volume(1)
                if pygame.Rect.colliderect(mouse_rect, pygame.Rect(94, 280, 253, 49)):
                    if sound_fx:
                        sound_fx = False
                    else:
                        sound_fx = True
                if pygame.Rect.colliderect(mouse_rect, pygame.Rect(94, 344, 253, 49)):
                    start_menu()

        clock.tick(FPS)
        pygame.display.update()


#  Main Menu
def start_menu():
    """ (None) -> None
        The main screen in the beginning.
    """
    if music:
        pygame.mixer.Channel(5).play(menu_music, -1)

    while True:
        display.blit(main_menu_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_rect = pygame.rect.Rect(mouse_x, mouse_y, 1, 1)
                if pygame.Rect.colliderect(mouse_rect, pygame.Rect(0, 400, 640, 450)):
                    bootcamp()
                if pygame.Rect.colliderect(mouse_rect, pygame.Rect(640, 400, 640, 450)):
                    survival()
                if pygame.Rect.colliderect(mouse_rect, pygame.Rect(1280, 400, 640, 450)):
                    settings()

        pygame.display.update()


if __name__ == '__main__':
    start_menu()
