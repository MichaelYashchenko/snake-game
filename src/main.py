import enum
import random

import pygame
from pygame import mixer

pygame.init()
pygame.display.set_caption('Snake')
screen = pygame.display.set_mode((640, 480))
fps = pygame.time.Clock()
running = True

# colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# background music
mixer.music.load('./music/Music.mp3')
pygame.mixer.music.set_volume(0.5)
mixer.music.play(-1)

score = 0


def play_sound(file_path):
    sound = mixer.Sound(file_path)
    sound.play()


def game_over(screen=screen):
    font = pygame.font.Font('freesansbold.ttf', 50)
    text = font.render('Game Over', True, RED)
    rect = text.get_rect()
    rect.center = (screen.get_width() // 2, screen.get_height() // 2)
    screen.blit(text, rect)
    play_sound('./music/Gameover.mp3')
    pygame.display.update()
    pygame.time.wait(3000)


def draw_score(score: int, screen=screen):
    font = pygame.font.Font('freesansbold.ttf', 20)
    text = font.render(f'Score: {score}', True, BLACK)
    rect = text.get_rect()
    rect.center = (screen.get_width() * 0.9, screen.get_height() * 0.1)
    screen.blit(text, rect)


class Apple(pygame.Vector2):
    def __init__(self, screen_obj):
        self._screen = screen_obj
        x, y = self._select_pos()
        super().__init__(x, y)

    def draw(self):
        pygame.draw.circle(self._screen, RED, self, 10)

    def change_pos(self):
        x, y = self._select_pos()
        self.x = x
        self.y = y

    def _select_pos(self):
        x = random.uniform(0, 1) * self._screen.get_width()
        y = random.uniform(0, 1) * self._screen.get_height()
        return x, y


class Direction(enum.Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class Snake:
    block_size = 20
    eps = 12

    def __init__(self, screen_obj):
        self._screen = screen_obj
        self.direction = Direction.UP
        self._body = [
            pygame.Vector2(
                self._screen.get_width() / 2 + self.block_size * i,
                self._screen.get_height() / 2,
            )
            for i in range(4)
        ]

    @property
    def head(self):
        return self._body[0]

    def move(self, keys):
        player_pos = self._body[0].copy()

        change_to = self.direction
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            change_to = Direction.UP
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            change_to = Direction.DOWN
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            change_to = Direction.LEFT
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            change_to = Direction.RIGHT

        if change_to == Direction.UP and self.direction != Direction.DOWN:
            self.direction = Direction.UP
        if change_to == Direction.DOWN and self.direction != Direction.UP:
            self.direction = Direction.DOWN
        if change_to == Direction.LEFT and self.direction != Direction.RIGHT:
            self.direction = Direction.LEFT
        if change_to == Direction.RIGHT and self.direction != Direction.LEFT:
            self.direction = Direction.RIGHT

        if self.direction == Direction.UP:
            player_pos.y -= self.block_size
        if self.direction == Direction.DOWN:
            player_pos.y += self.block_size
        if self.direction == Direction.LEFT:
            player_pos.x -= self.block_size
        if self.direction == Direction.RIGHT:
            player_pos.x += self.block_size

        self._body.insert(0, player_pos)

    def pop_tail(self):
        self._body.pop()

    def draw(self):
        for block in self._body:
            x = block.x - self.block_size // 2
            y = block.y - self.block_size // 2
            pygame.draw.rect(
                self._screen,
                GREEN,
                (x, y, self.block_size, self.block_size),
            )

    def is_close(self, apple_vec: Apple):
        return self.head.distance_to(apple_vec) < self.eps

    def cross_the_border(self):
        return (
            self.head.x < 0 or
            self.head.x > self._screen.get_width() or
            self.head.y < 0 or
            self.head.y > self._screen.get_height()
        )

    def eat_tail(self):
        res = False
        if len(self._body) < 2:
            return res
        for block in self._body[1:]:
            res = res or self.head.distance_to(block) < self.eps
        return res


apple = Apple(screen)
snake = Snake(screen)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if (
            # Если вышли за границы, игра заканчивается
            snake.cross_the_border() or
            # Если врезались в хвост, игра заканчивается
            snake.eat_tail()
    ):
        game_over()
        running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_ESCAPE]:
        running = False
    snake.move(keys)
    screen.fill(WHITE)
    if snake.is_close(apple):
        score += 1
        apple.change_pos()
        play_sound('./music/Pickup.mp3')
    else:
        snake.pop_tail()
    apple.draw()
    snake.draw()
    draw_score(score)
    pygame.display.update()
    fps.tick(10)

pygame.quit()
