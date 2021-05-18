import random
import sys
from os.path import abspath, dirname
import pygame

pygame.init()

BASE_PATH = abspath(dirname(__file__))
FONT_PATH = BASE_PATH + "/fonts/"
IMAGE_PATH = BASE_PATH + "/images/"
SOUND_PATH = BASE_PATH + "/sounds/"

# Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (210, 0, 255)
CYAN = (0, 255, 255)
GREEN = (78, 255, 87)
RED = (237, 28, 36)

SCREEN = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Space Invaders")
icon = pygame.image.load(IMAGE_PATH + "ufo.png")
pygame.display.set_icon(icon)

FONT = FONT_PATH + "space_invaders.ttf"
TITLE_FONT = pygame.font.Font(FONT, 50)
SUB_TITLE_FONT = pygame.font.Font(FONT, 25)
MAIN_FONT = pygame.font.Font(FONT, 20)

BACKGROUND = pygame.image.load(IMAGE_PATH + "background.jpeg")
IMG_NAMES = [
    "ship",
    "laser",
    "explosionpurple",
    "explosioncyan",
    "explosiongreen",
    "mystery",
    "enemy1_2",
    "enemy2_1",
    "enemy3_1",
]
IMAGES = {
    name: pygame.image.load(IMAGE_PATH + "{}.png".format(name)).convert_alpha()
    for name in IMG_NAMES
}

SOUND_NAMES = [
    "background",
    "shoot",
    "invaderkilled",
    "mysteryentered",
    "mysterykilled",
]
SOUNDS = {
    name: pygame.mixer.Sound(SOUND_PATH + "{}.wav".format(name))
    for name in SOUND_NAMES
}

EXPLOSION_PURPLE = pygame.transform.scale(
    IMAGES["explosionpurple"].convert_alpha(), (50, 40)
)
EXPLOSION_CYAN = pygame.transform.scale(
    IMAGES["explosioncyan"].convert_alpha(), (50, 40)
)
EXPLOSION_GREEN = pygame.transform.scale(
    IMAGES["explosiongreen"].convert_alpha(), (50, 40)
)
MYSTERY_IMG = pygame.transform.scale(
    IMAGES["mystery"].convert_alpha(), (90, 40)
)


class Ship:
    def __init__(self):
        self.image = IMAGES["ship"]
        self.middle = int((740 + 10) / 2)
        self.y_position = 540
        self.rect = self.image.get_rect(topleft=(self.middle, self.y_position))
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.speed
        SCREEN.blit(self.image, self.rect)


class Bullet:
    def __init__(self):
        self.image = IMAGES["laser"]
        self.sound = SOUNDS["shoot"]
        self.x_pos = 0
        self.y_pos = 540
        self.rect = self.update_rectangle()
        self.speed = 11
        self.state = "Ready"

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            if self.state == "Ready":
                self.state = "Fire"
                self.fire()

        if self.y_pos <= 0:
            self.state = "Ready"
        if self.state == "Fire":
            self.draw()
            self.y_pos -= self.speed
        self.rect = self.update_rectangle()

    def update_rectangle(self):
        return self.image.get_rect(topleft=(self.x_pos + 23, self.y_pos))

    def fire(self):
        self.y_pos = 540
        self.sound.set_volume(0.05)
        self.sound.play()
        self.x_pos = player.rect.x

    def draw(self):
        self.state = "Fire"
        SCREEN.blit(self.image, (self.x_pos + 23, self.y_pos))


class Enemies:
    score = 0

    def __init__(self):
        self.num_in_a_row = 10
        self.total_num = 50
        self.speed = 1
        self.move_y_pos = 10
        self.purple = pygame.transform.scale(IMAGES["enemy1_2"], (40, 40))
        self.cyan = pygame.transform.scale(IMAGES["enemy2_1"], (40, 40))
        self.green = pygame.transform.scale(IMAGES["enemy3_1"], (40, 40))
        self.p_img = []
        self.c_img = []
        self.g_img = []
        self.purple_hit = []
        self.cyan_hit = [[], []]
        self.green_hit = [[], []]
        self.purple_rect = []
        self.cyan_rect = [[], []]
        self.green_rect = [[], []]
        self.rects = [
            self.purple_rect,
            self.cyan_rect[0],
            self.cyan_rect[1],
            self.green_rect[0],
            self.green_rect[1],
        ]
        self.p_rect = self.purple.get_rect(topleft=(155, 80))
        self.c_rect = self.purple.get_rect(topleft=(155, 120))
        self.g_rect = self.green.get_rect(topleft=(155, 160))

    def enemies_generator(self):
        x = 105
        for enemy in range(self.num_in_a_row):
            x += 50
            self.p_img.append(self.purple)
            self.c_img.append(self.cyan)
            self.g_img.append(self.green)

            images = [
                self.p_img[enemy],
                self.c_img[enemy],
                self.c_img[enemy],
                self.g_img[enemy],
                self.g_img[enemy],
            ]
            hits = [
                self.purple_hit,
                self.cyan_hit[0],
                self.cyan_hit[1],
                self.green_hit[0],
                self.green_hit[1],
            ]

            y = 40
            for rect, image, hit in zip(self.rects, images, hits):
                rect.append(image.get_rect(topleft=(x, y)))
                y += 50
                hit.append(False)

    def moving(self, enemy_rect):
        for num in enemy_rect:
            num.x += self.speed

    def border_collision_push_y_pos(self, enemy_rect, enemy_img):
        for i in range(self.num_in_a_row):
            for rect in enemy_rect:
                if rect.x <= 1:
                    self.speed = 1
                    enemy_rect[i].y += self.move_y_pos
                elif rect.x >= 755:
                    self.speed = -1
                    enemy_rect[i].y += self.move_y_pos
            SCREEN.blit(enemy_img[i], enemy_rect[i])

    def move_enemies_check_border(self):
        images = [self.p_img, self.c_img, self.c_img, self.g_img, self.g_img]
        for rect in self.rects:
            self.moving(rect)
        for rect, img in zip(self.rects, images):
            self.border_collision_push_y_pos(rect, img)

    def hide_enemies(self, enemy_rect, explosion_color, enemy_hit):
        if bullet.state != "Fire":
            return
        for j in range(self.num_in_a_row):
            if not rect_intersect(bullet.rect, enemy_rect[j]):
                continue
            self.kill_enemy(enemy_rect, explosion_color, enemy_hit, j)

    def kill_enemy(self, enemy_rect, explosion_color, enemy_hit, j):
        Explosion(explosion_color, enemy_rect[j].x, enemy_rect[j].y)
        SOUNDS["invaderkilled"].set_volume(0.05)
        SOUNDS["invaderkilled"].play()
        enemy_rect[j].y = 600
        bullet.state = "Ready"
        enemy_hit[j] = True
        self.score += 30
        self.total_num -= 1

    def enemies_collision(self):
        self.hide_enemies(self.purple_rect, EXPLOSION_PURPLE, self.purple_hit)
        self.hide_enemies(self.cyan_rect[0], EXPLOSION_CYAN, self.cyan_hit[0])
        self.hide_enemies(self.cyan_rect[1], EXPLOSION_CYAN, self.cyan_hit[1])
        self.hide_enemies(
            self.green_rect[0], EXPLOSION_GREEN, self.green_hit[0]
        )
        self.hide_enemies(
            self.green_rect[1], EXPLOSION_GREEN, self.green_hit[1]
        )

    def is_enemy_hit_ship(self):
        for i in range(self.num_in_a_row):
            if (
                self.purple_rect[i].y >= 410
                and self.purple_hit[i] is not True
                or self.cyan_rect[0][i].y >= 410
                and self.cyan_hit[0][i] is not True
                or self.cyan_rect[1][i].y >= 410
                and self.cyan_hit[1][i] is not True
                or self.green_rect[0][i].y >= 410
                and self.green_hit[0][i] is not True
                or self.green_rect[1][i].y >= 410
                and self.green_hit[1][i] is not True
            ):
                return True
        return False


class Explosion:
    explosions_list = []

    def __init__(self, explosion_color, enemy_rect_x, enemy_rect_y):
        self.explosion_color = explosion_color
        self.enemy_rect_x = enemy_rect_x
        self.enemy_rect_y = enemy_rect_y
        self.counter = 5
        Explosion.explosions_list.append(self)

    def update(self):
        if self.counter > 0:
            SCREEN.blit(
                self.explosion_color, (self.enemy_rect_x, self.enemy_rect_y)
            )
            self.counter -= 1
        elif self.counter == 0:
            Explosion.explosions_list.remove(self)

    @staticmethod
    def update_all_explosions():
        for explosion in Explosion.explosions_list:
            explosion.update()


class Bunker:
    def __init__(self):
        self.bunker_empty = [[], [], [], []]
        self.bunker_row = [[], [], [], []]

    @staticmethod
    def draw_bunker(row_empty, row_bunker, x_axis, y):
        for row in range(9):
            if row in row_empty:
                continue
            first_x = x_axis + row * 10
            row_bunker.append(
                pygame.draw.rect(SCREEN, GREEN, (first_x, y, 10, 10))
            )

    def all_bunker(self):
        y_bunker = 440
        for i in range(4):
            y_bunker += 10
            bunker_y = [70, 350, 650]
            for k in range(3):
                self.draw_bunker(
                    bunker[k].bunker_empty[i],
                    bunker[k].bunker_row[i],
                    bunker_y[k],
                    y_bunker,
                )
                self.draw_bunker(
                    bunker[k].bunker_empty[i],
                    bunker[k].bunker_row[i],
                    bunker_y[k],
                    y_bunker,
                )
                self.draw_bunker(
                    bunker[k].bunker_empty[i],
                    bunker[k].bunker_row[i],
                    bunker_y[k],
                    y_bunker,
                )

    @staticmethod
    def hide_rectangle_pixel(row_bunker, bunker_empty):
        if bullet.state != "Fire":
            return
        for k in range(9):
            if not rect_intersect(bullet.rect, row_bunker[k]):
                continue
            bunker_empty.append(k)
            bullet.state = "Ready"
            row_bunker[k].y = 600
            row_bunker[k].x = 600

    def bunker_collision(self):
        for i in range(4):
            for j in range(3):
                self.hide_rectangle_pixel(
                    bunker[j].bunker_row[i], bunker[j].bunker_empty[i]
                )
                self.hide_rectangle_pixel(
                    bunker[j].bunker_row[i], bunker[j].bunker_empty[i]
                )
                self.hide_rectangle_pixel(
                    bunker[j].bunker_row[i], bunker[j].bunker_empty[i]
                )


class MysteryState:
    def __init__(self, mystery_rect, yaxis):
        self.mystery_rect = mystery_rect
        self.mystery_entered_played = False
        self.mystery_is_visible = False
        self.yaxis = yaxis
        self.speed = 2

    def show_mystery(self):
        if self.mystery_is_visible:
            if not self.mystery_entered_played:
                SOUNDS["mysteryentered"].set_volume(0.03)
                SOUNDS["mysteryentered"].play()
                self.mystery_entered_played = True
            if self.mystery_rect.x >= 800:
                self.mystery_rect.x = 900
            else:
                self.mystery_rect.x += self.speed
                SCREEN.blit(MYSTERY_IMG, self.mystery_rect)

    def draw_mystery(self):
        self.mystery_is_visible = False
        for v in range(enemies.num_in_a_row):
            if self.yaxis <= enemies.purple_rect[v].y <= 300:
                self.mystery_is_visible = True
            if self.yaxis <= enemies.purple_rect[v].y <= 300:
                self.mystery_is_visible = True

        self.show_mystery()

        if rect_intersect(bullet.rect, self.mystery_rect):
            self.random_point_mystery(self.mystery_rect)

    @staticmethod
    def random_point_mystery(m_rect):
        random_point = random.randint(1, 6) * 50
        point_text = MAIN_FONT.render(str(random_point), True, WHITE)
        m_rect.x += 23
        SOUNDS["mysterykilled"].set_volume(0.05)
        SOUNDS["mysterykilled"].play()
        SCREEN.blit(point_text, m_rect)
        m_rect.x = 900
        enemies.score += random_point


class GameOver:
    @staticmethod
    def draw_next_round():
        SCREEN.blit(BACKGROUND, (0, 0))
        game_over_text = TITLE_FONT.render(
            "Next Round Coming soon!", True, WHITE
        )
        SCREEN.blit(game_over_text, (25, 250))
        SOUNDS["background"].stop()
        SOUNDS["shoot"].stop()

    @staticmethod
    def draw_game_over():
        SCREEN.blit(BACKGROUND, (0, 0))
        game_over_text = TITLE_FONT.render("Game Over", True, WHITE)
        SCREEN.blit(game_over_text, (250, 250))
        SOUNDS["background"].stop()
        SOUNDS["shoot"].stop()

    @staticmethod
    def is_game_over():
        if enemies.total_num == 0:
            return True
        return False


class RoundOne:
    @staticmethod
    def draw_main():
        CLOCK.tick(FPS)
        SCREEN.fill(BLACK)
        SCREEN.blit(BACKGROUND, (0, 0))

        lives_text = MAIN_FONT.render("Lives", True, WHITE)
        tiny_enemy = pygame.transform.scale(IMAGES["ship"], (25, 25))
        score_text = MAIN_FONT.render("Score", True, WHITE)
        score_text_num = MAIN_FONT.render(str(enemies.score), True, GREEN)

        SCREEN.blit(lives_text, (640, 5))
        SCREEN.blit(tiny_enemy, (715, 3))
        SCREEN.blit(tiny_enemy, (742, 3))
        SCREEN.blit(tiny_enemy, (769, 3))
        SCREEN.blit(score_text, (5, 5))
        SCREEN.blit(score_text_num, (85, 5))

        player.update()
        bullet.update()
        enemies.enemies_collision()
        bunker[0].bunker_collision()
        enemies.move_enemies_check_border()
        bunker[0].all_bunker()
        state_one.draw_mystery()
        state_two.draw_mystery()
        Explosion.update_all_explosions()

    def main(self):
        pygame.key.set_repeat(1, 10)
        SOUNDS["background"].set_volume(0.5)
        SOUNDS["background"].play(-1)

        while True:
            self.draw_main()

            if game_over.is_game_over():
                game_over.draw_next_round()
            elif enemies.is_enemy_hit_ship():
                game_over.draw_game_over()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            pygame.display.update()


bunker = [Bunker(), Bunker(), Bunker()]
player = Ship()
bullet = Bullet()
enemies = Enemies()
enemies.enemies_generator()
state_one = MysteryState(MYSTERY_IMG.get_rect(topleft=(-100, 40)), 110)
state_two = MysteryState(MYSTERY_IMG.get_rect(topleft=(-100, 60)), 150)
game_over = GameOver()
round_one = RoundOne()

CLOCK = pygame.time.Clock()
FPS = 60


def rect_intersect(rect_zero, rect_one):
    return rect_zero.colliderect(rect_one)


def main_menu():
    while True:
        CLOCK.tick(FPS)

        title_text = TITLE_FONT.render("Space Invaders", True, WHITE)
        title_text2 = SUB_TITLE_FONT.render(
            "Press enter to continue", True, WHITE
        )
        point_text_green = SUB_TITLE_FONT.render("   =   10 pts", True, GREEN)
        point_text_cyan = SUB_TITLE_FONT.render("   =   20 pts", True, CYAN)
        point_text_purple = SUB_TITLE_FONT.render("   =   30 pts", True, PURPLE)
        point_text_red = SUB_TITLE_FONT.render("   =  ?????", True, RED)

        SCREEN.blit(BACKGROUND, (0, 0))
        SCREEN.blit(title_text, (164, 155))
        SCREEN.blit(title_text2, (201, 225))
        SCREEN.blit(enemies.g_img[0], (300, 265))
        SCREEN.blit(point_text_green, (350, 270))
        SCREEN.blit(enemies.c_img[0], (300, 315))
        SCREEN.blit(point_text_cyan, (350, 320))
        SCREEN.blit(enemies.p_img[0], (300, 365))
        SCREEN.blit(point_text_purple, (350, 370))
        SCREEN.blit(MYSTERY_IMG, (275, 420))
        SCREEN.blit(point_text_red, (350, 420))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    round_one.main()

        pygame.display.update()


if __name__ == "__main__":
    main_menu()
