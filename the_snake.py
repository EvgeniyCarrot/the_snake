from random import choice

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

KEY_TO_DIRECTION = {
    pygame.K_UP: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_RIGHT: RIGHT,
}

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 20

ALL_CELLS = [
    (x * GRID_SIZE, y * GRID_SIZE)
    for x in range(GRID_WIDTH)
    for y in range(GRID_HEIGHT)
]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pygame.display.set_caption('Змейка')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, position=None, body_color=None):
        """Инициализирует базовый игровой объект."""
        default_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position or default_pos
        self.body_color = body_color

    def draw(self):
        """Отрисовывает объект на поверхности.

        Базовый класс не знает, как рисовать фигуру, поэтому метод пуст.
        """
        pass

    @staticmethod
    def draw_cell(surface, position, color, border_color=None):
        """Отрисовывает одну ячейку заданного цвета."""
        rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, color, rect)
        if border_color:
            pygame.draw.rect(surface, border_color, rect, 1)


class Apple(GameObject):
    """Класс, описывающий яблоко."""

    def __init__(self):
        """Инициализирует яблоко со случайной позицией и красным цветом."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self, snake_positions=None):
        """Устанавливает случайную позицию яблока, не занятую змейкой."""
        occupied = set(snake_positions) if snake_positions else set()
        free_cells = tuple(set(ALL_CELLS) - occupied)
        self.position = choice(free_cells) if free_cells else choice(ALL_CELLS)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(screen, self.position, self.body_color, BORDER_COLOR)


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self):
        """Инициализирует змейку с начальной длиной 1 в центре экрана."""
        start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(position=start_pos, body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [start_pos]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки на следующее."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки, добавляя голову и удаляя хвост."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Отрисовывает змейку на игровом поле и затирает след."""
        for position in self.positions[:-1]:
            self.draw_cell(screen, position, self.body_color, BORDER_COLOR)

        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.position = start_pos
        self.positions = [start_pos]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш для изменения направления движения."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False

            new_dir = KEY_TO_DIRECTION.get(event.key)
            if new_dir:
                current_dir = game_object.direction
                opposite = OPPOSITE_DIRECTIONS.get(current_dir)
                if new_dir != opposite:
                    game_object.next_direction = new_dir
    return True


def main():
    """Основная функция игры, содержащая игровой цикл."""
    pygame.init()

    snake = Snake()
    apple = Apple()

    running = True

    while running:
        clock.tick(SPEED)

        if not handle_keys(snake):
            running = False
            continue

        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)

        head_pos = snake.get_head_position()
        is_collision = head_pos in snake.positions[1:]

        if len(snake.positions) > 3 and is_collision:
            snake.reset()
            apple.randomize_position(snake.positions)

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()
