import random
from typing import List, Optional, Tuple

import pygame

# Константы игры
GRID_SIZE = 20
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

BOARD_BACKGROUND_COLOR = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Направления движения
RIGHT = 'RIGHT'
LEFT = 'LEFT'
UP = 'UP'
DOWN = 'DOWN'

# Инициализация Pygame и глобальные объекты
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(
        self,
        position: Optional[Tuple[int, int]] = None,
        color: Tuple[int, int, int] = (255, 255, 255)
    ):
        """
        Инициализация базового игрового объекта.

        :param position: Начальная позиция объекта в пикселях.
        :param color: Цвет объекта в формате RGB.
        """
        if position is None:
            position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.position = position
        self.body_color = color

    def draw(self, surface: pygame.Surface) -> None:
        """
        Абстрактный метод отрисовки объекта.

        :param surface: Поверхность Pygame для рисования.
        """
        raise NotImplementedError('Метод draw должен быть реализован')


class Apple(GameObject):
    """Класс яблока на игровом поле."""

    def __init__(self) -> None:
        """Инициализирует яблоко со случайной позицией."""
        super().__init__(color=RED)
        self.randomize_position()

    def randomize_position(
        self,
        snake_positions: Optional[List[Tuple[int, int]]] = None
    ) -> None:
        """
        Устанавливает случайную позицию яблока.

        :param snake_positions: Список координат сегментов змейки.
        """
        while True:
            x = random.randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            new_pos = (x, y)
            if snake_positions is None or new_pos not in snake_positions:
                self.position = new_pos
                break

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает яблоко как залитый квадрат."""
        pygame.draw.rect(
            surface,
            self.body_color,
            (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        )


class Snake(GameObject):
    """Класс змейки, управляемой игроком."""

    def __init__(self) -> None:
        """Инициализирует змейку в начальном состоянии."""
        start_x = (GRID_WIDTH // 2) * GRID_SIZE
        start_y = (GRID_HEIGHT // 2) * GRID_SIZE
        super().__init__((start_x, start_y), GREEN)
        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [(start_x, start_y)]
        self.direction: str = RIGHT
        self.next_direction: Optional[str] = None
        self.last: Optional[Tuple[int, int]] = None
        self.grow: bool = False

    def update_direction(self) -> None:
        """Обновляет направление движения с учётом запрета на разворот."""
        if self.next_direction is not None:
            if (self.next_direction == RIGHT and self.direction != LEFT) or \
               (self.next_direction == LEFT and self.direction != RIGHT) or \
               (self.next_direction == UP and self.direction != DOWN) or \
               (self.next_direction == DOWN and self.direction != UP):
                self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """
        Перемещает змейку на одну клетку.
        Реализует появление с противоположной стороны при достижении границ.
        """
        head_x, head_y = self.get_head_position()

        if self.direction == RIGHT:
            new_head_grid = (
                (head_x // GRID_SIZE + 1) % GRID_WIDTH,
                head_y // GRID_SIZE
            )
        elif self.direction == LEFT:
            new_head_grid = (
                (head_x // GRID_SIZE - 1) % GRID_WIDTH,
                head_y // GRID_SIZE
            )
        elif self.direction == UP:
            new_head_grid = (
                head_x // GRID_SIZE,
                (head_y // GRID_SIZE - 1) % GRID_HEIGHT
            )
        elif self.direction == DOWN:
            new_head_grid = (
                head_x // GRID_SIZE,
                (head_y // GRID_SIZE + 1) % GRID_HEIGHT
            )
        else:
            raise ValueError(f'Неизвестное направление: {self.direction}')

        new_head = (new_head_grid[0] * GRID_SIZE, new_head_grid[1] * GRID_SIZE)

        if new_head in self.positions:
            self.reset()
            return

        if not self.grow and len(self.positions) > 0:
            self.last = self.positions[-1]
        else:
            self.last = None

        self.positions.insert(0, new_head)

        if self.grow:
            self.length += 1
            self.grow = False
        else:
            if len(self.positions) > self.length:
                self.positions.pop()

    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовывает змейку и стирает след."""
        if self.last is not None:
            pygame.draw.rect(
                surface,
                BOARD_BACKGROUND_COLOR,
                (self.last[0], self.last[1], GRID_SIZE, GRID_SIZE)
            )

        for pos in self.positions:
            pygame.draw.rect(
                surface,
                self.body_color,
                (pos[0], pos[1], GRID_SIZE, GRID_SIZE)
            )

    def get_head_position(self) -> Tuple[int, int]:
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        start_x = (GRID_WIDTH // 2) * GRID_SIZE
        start_y = (GRID_HEIGHT // 2) * GRID_SIZE
        self.positions = [(start_x, start_y)]
        self.direction = random.choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None
        self.grow = False
        self.last = None


def handle_keys(snake: Snake) -> None:
    """
    Обрабатывает нажатия клавиш для управления змейкой.

    :param snake: Объект змейки.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN


def main() -> None:
    """Главный игровой цикл."""
    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    while True:
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow = True
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw(screen)
        snake.draw(screen)

        pygame.display.update()
        clock.tick(20)


if __name__ == '__main__':
    main()