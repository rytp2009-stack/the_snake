from random import choice, randint

import pygame

# Константы для размеров экрана и сетки
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения
UP = (0, -GRID_SIZE)
DOWN = (0, GRID_SIZE)
LEFT = (-GRID_SIZE, 0)
RIGHT = (GRID_SIZE, 0)

# Цвета
BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

# Скорость игры
SPEED = 10

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализация базового игрового объекта."""
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """Абстрактный метод для отрисовки объекта."""
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(self):
        """Инициализация яблока со случайной позицией."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайное положение яблока на игровом поле."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self, surface):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(
            self.position[0],
            self.position[1],
            GRID_SIZE,
            GRID_SIZE
        )
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self):
        """Инициализация начального состояния змейки."""
        super().__init__(body_color=SNAKE_COLOR)
        self.reset()

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки."""
        # Получаем текущую позицию головы
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Вычисляем новую позицию головы с учетом оборачивания
        new_head = (
            (head_x + dx) % SCREEN_WIDTH,
            (head_y + dy) % SCREEN_HEIGHT
        )

        # Проверяем столкновение с собой
        if len(self.positions) > 2 and new_head in self.positions[2:]:
            self.reset()
        else:
            # Добавляем новую голову в начало списка
            self.positions.insert(0, new_head)

            # Если длина змейки превышает установленную, удаляем хвост
            if len(self.positions) > self.length:
                self.last = self.positions.pop()
            else:
                self.last = None

    def draw(self, surface):
        """Отрисовывает змейку на экране."""
        # Отрисовка тела змейки (кроме головы)
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        if self.positions:
            head_rect = pygame.Rect(
                self.positions[0],
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(surface, self.body_color, head_rect)
            pygame.draw.rect(surface, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None
        self.last = None
        # Очищаем экран
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для изменения направления движения."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Основной цикл игры."""
    # Создаем объекты игры
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        # Обрабатываем ввод пользователя
        handle_keys(snake)

        # Обновляем направление движения
        snake.update_direction()

        # Двигаем змейку
        snake.move()

        # Проверяем, съела ли змейка яблоко
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        # Отрисовываем объекты
        snake.draw(screen)
        apple.draw(screen)

        # Обновляем экран
        pygame.display.update()


if __name__ == '__main__':
    main()
