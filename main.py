import random
import time

import pygame


class MainScreen:
    def __init__(self, screen, completed_levels, game):
        """Инициализация главного экрана"""
        self.screen = screen
        self.completed_levels = completed_levels
        self.game = game  # Сохраняем ссылку на игру
        self.background_layers = [
            pygame.image.load("textures/background/BG1.png").convert_alpha(),
            pygame.image.load("textures/background/BG2.png").convert_alpha(),
            pygame.image.load("textures/background/BG3.png").convert_alpha()
        ]
        self.font_small = pygame.font.Font("textures/font/Aladin-Regular.ttf", 30)
        self.font_large = pygame.font.Font("textures/font/Aladin-Regular.ttf", 60)

    def draw(self):
        """Отрисовка всех слоев фона"""
        for layer in self.background_layers:
            layer = pygame.transform.scale(layer, (800, 600))
            self.screen.blit(layer, (0, 0))

        text_top = self.font_small.render("Developer: UnRobWarrior", True, (255, 255, 255))
        self.screen.blit(text_top, (10, 10))

        text_title = self.font_large.render("The lost ghost", True, (255, 255, 255))
        text_rect = text_title.get_rect(center=(400, 200))
        self.screen.blit(text_title, text_rect)

        button_texts = ["Desert", "Ocean", "Hell"]
        for i, text in enumerate(button_texts):
            color = (100, 100, 100)
            if text in self.completed_levels or text == "Desert":
                color = (255, 255, 255)
            button = self.font_small.render(text, True, color)
            button_rect = button.get_rect(center=(400, 300 + i * 50))
            self.screen.blit(button, button_rect)

    def handle_click(self, x, y):
        """Обработка кликов"""
        if 350 < x < 450:
            if 285 < y < 315:
                self.game.start_level("Desert")

    def update(self):
        """Обновление экрана"""
        self.draw()
        pygame.display.flip()


class Player:
    def __init__(self, x, y):
        self.x = x * 40  # Преобразуем координаты из клеток в пиксели
        self.y = y * 40
        self.speed = 10  # Скорость движения
        self.velocity_x = 0
        self.velocity_y = 0

        # Загрузка кадров анимации
        fremes = [pygame.image.load(f"textures/player/walk/Playerwalk{i}.png").convert_alpha() for i in range(1, 6)]
        self.frames_right = list()
        for i in fremes:
            i = pygame.transform.scale(i, (35, 35))
            self.frames_right.append(i)
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]
        self.frames_up = self.frames_right  # Можно добавить отдельную анимацию вверх
        self.frames_down = self.frames_right  # Можно добавить отдельную анимацию вниз

        # Текстура для состояния покоя
        self.idle_frame = pygame.transform.scale(pygame.image.load("textures/player/PlayerIdle.png").convert_alpha(),
                                                 (35, 35))

        self.current_frames = self.frames_down  # По умолчанию используем кадры для движения вниз
        self.current_frame_index = 0
        self.animation_speed = 0.2  # Скорость анимации (кадры в секунду)
        self.last_update = pygame.time.get_ticks()
        self.is_moving = False  # Флаг движения

    def handle_input(self, event):
        """Обрабатывает нажатия клавиш"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.velocity_y = -self.speed
                self.current_frames = self.frames_up
            elif event.key == pygame.K_s:
                self.velocity_y = self.speed
                self.current_frames = self.frames_down
            elif event.key == pygame.K_a:
                self.velocity_x = -self.speed
                self.current_frames = self.frames_left
            elif event.key == pygame.K_d:
                self.velocity_x = self.speed
                self.current_frames = self.frames_right

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_s):
                self.velocity_y = 0
            elif event.key in (pygame.K_a, pygame.K_d):
                self.velocity_x = 0

    def update(self, level_map):
        """Обновляет позицию игрока, проверяя столкновения"""
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y

        # Двигаем игрока отдельно по X и Y, если нет коллизии
        if not self.check_collision(new_x, self.y, level_map):
            self.x = new_x

        if not self.check_collision(self.x, new_y, level_map):
            self.y = new_y

        # Определяем, движется ли игрок
        self.is_moving = self.velocity_x != 0 or self.velocity_y != 0

        # Обновление анимации только если игрок двигается
        if self.is_moving:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed * 1000:
                self.last_update = now
                self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)

    def check_collision(self, x, y, level_map):
        """Проверяет, есть ли перед игроком стена с уменьшенным хитбоксом"""
        hitbox_offset = 5  # Отступ с каждой стороны (уменьшение хитбокса)
        hitbox_size = 30  # Новый размер хитбокса

        # Четыре точки по краям уменьшенного хитбокса
        corners = [
            (int((x + hitbox_offset) // 40), int((y + hitbox_offset) // 40)),  # Верхний левый угол
            (int((x + hitbox_offset + hitbox_size) // 40), int((y + hitbox_offset) // 40)),  # Верхний правый
            (int((x + hitbox_offset) // 40), int((y + hitbox_offset + hitbox_size) // 40)),  # Нижний левый
            (int((x + hitbox_offset + hitbox_size) // 40), int((y + hitbox_offset + hitbox_size) // 40))
            # Нижний правый
        ]

        for grid_x, grid_y in corners:
            if level_map[grid_y][grid_x] == '1':  # Стена
                return True

        return False

    def draw(self, screen, camera):
        """Рисует игрока с учетом смещения камеры"""
        screen_x, screen_y = camera.apply(self)
        if self.is_moving:
            current_frame = self.current_frames[self.current_frame_index]
        else:
            current_frame = self.idle_frame  # Если игрок стоит, рисуем Idle-кадр

        screen.blit(current_frame, (screen_x, screen_y))


class Enemy:
    def __init__(self, x, y):
        self.x = x * 40  # Преобразуем координаты в пиксели
        self.y = y * 40
        self.speed = 2  # Скорость движения
        self.direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])  # Рандомное направление

        # Загрузка анимаций
        frames = [pygame.image.load(f"textures/enemy/Enemywalk{i}.png").convert_alpha() for i in range(1, 6)]
        self.frames_right = [pygame.transform.scale(frame, (35, 35)) for frame in frames]
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]
        self.frames_up = self.frames_right  # Если будут разные анимации - замени
        self.frames_down = self.frames_right

        self.current_frames = self.frames_down  # По умолчанию идет вниз
        self.current_frame_index = 0
        self.animation_speed = 0.2  # Скорость анимации
        self.last_update = pygame.time.get_ticks()

    def update(self, level_map):
        """Обновляет движение врага и анимацию"""
        new_x = self.x + self.direction[0] * self.speed
        new_y = self.y + self.direction[1] * self.speed

        if not self.check_collision(new_x, new_y, level_map):
            self.x = new_x
            self.y = new_y
        else:
            self.change_direction()

        # Обновление анимации
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)

        # Обновляем анимацию
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed * 1000:
            self.last_update = now
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)

    def change_direction(self):
        """Меняет направление движения при столкновении"""
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        directions.remove(self.direction)  # Исключаем текущее направление
        self.direction = random.choice(directions)

        # Обновляем текущую анимацию
        if self.direction == (1, 0):  # Вправо
            self.current_frames = self.frames_right
        elif self.direction == (-1, 0):  # Влево
            self.current_frames = self.frames_left
        elif self.direction == (0, -1):  # Вверх
            self.current_frames = self.frames_up
        elif self.direction == (0, 1):  # Вниз
            self.current_frames = self.frames_down

    def check_collision(self, x, y, level_map):
        """Проверяет, столкнулся ли враг со стеной"""
        enemy_rect = pygame.Rect(x, y, 40, 40)  # Хитбокс врага

        for row_idx, row in enumerate(level_map):
            for col_idx, tile in enumerate(row):
                if tile == '1':  # Стены
                    wall_rect = pygame.Rect(col_idx * 40, row_idx * 40, 40, 40)
                    if enemy_rect.colliderect(wall_rect):  # Проверка пересечения
                        return True
        return False

    def draw(self, screen, camera):
        """Рисует врага на экране с учетом камеры"""
        screen_x, screen_y = camera.apply(self)
        screen.blit(self.current_frames[self.current_frame_index], (screen_x, screen_y))


class Camera:
    def __init__(self, width, height):
        self.offset_x = 0
        self.offset_y = 0
        self.width = width
        self.height = height

    def update(self, player):
        """Следит за игроком и обновляет смещение"""
        self.offset_x = player.x - self.width // 2
        self.offset_y = player.y - self.height // 2

    def apply(self, entity):
        """Возвращает координаты сущности с учетом смещения камеры"""
        return entity.x - self.offset_x, entity.y - self.offset_y

    def apply_tile(self, x, y, tile_size):
        """Возвращает координаты тайла с учетом камеры"""
        return x * tile_size - self.offset_x, y * tile_size - self.offset_y


class DesertLevel:
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game  # Сохраняем ссылку на объект Game
        self.tile_size = 40
        self.start_time = time.time()
        self.load_textures()
        self.load_map("data/levels/desert_level_map.txt")

        # Создаем камеру
        self.camera = Camera(screen.get_width(), screen.get_height())

        # Ищем стартовую позицию игрока
        self.player = None
        self.enemies = []  # Список врагов

        self.is_game_over = False  # Флаг завершения уровня

        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile == '@':
                    self.player = Player(x, y)
                    self.map_data[y][x] = '0'
                elif tile == '*':  # Враг
                    self.enemies.append(Enemy(x, y))
                    self.map_data[y][x] = '0'  # Очищаем клетку

    def load_textures(self):
        """Загрузка текстур"""
        self.textures = {
            '1': pygame.image.load("textures/levels/Desert/wall.png").convert_alpha(),  # Стена
            '0': pygame.image.load("textures/levels/Desert/path.png").convert_alpha(),  # Проход
            '2': pygame.image.load("textures/levels/Desert/exit.png").convert_alpha(),  # Выход
            '@': pygame.image.load("textures/levels/Desert/path.png").convert_alpha(),  # Игрок (будет заменён на класс)
            '#': pygame.image.load("textures/levels/Desert/path.png").convert_alpha(),
            # Зелье (будет заменено на класс)
            '*': pygame.image.load("textures/levels/Desert/path.png").convert_alpha()  # Враг (будет заменён на класс)
        }

    def load_map(self, filename):
        """Загрузка карты"""
        with open(filename, "r") as file:
            self.map_data = [list(line.strip()) for line in file]

    def handle_events(self, event):
        """Передает события игроку"""
        self.player.handle_input(event)

    def update(self):
        """Обновляет состояние уровня"""
        if self.is_game_over:  # Если уровень завершён, прекращаем обновление
            return

        self.player.update(self.map_data)
        self.camera.update(self.player)  # Камера следует за игроком

        for enemy in self.enemies:
            enemy.update(self.map_data)

        self.check_defeat()  # Проверяем поражение
        self.check_victory()  # Проверяем победу

        self.draw()
        pygame.display.flip()

    def draw(self):
        """Отрисовка уровня с учетом камеры"""
        self.screen.fill((0, 0, 0))
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                texture = pygame.transform.scale(self.textures.get(tile, self.textures['0']), (40, 40))
                screen_x, screen_y = self.camera.apply_tile(x, y, self.tile_size)
                self.screen.blit(texture, (screen_x, screen_y))

        self.player.draw(self.screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)  # Отрисовываем врагов

        self.draw_timer()

    def draw_timer(self):
        """Отрисовка таймера"""
        elapsed_time = int(time.time() - self.start_time)
        font = pygame.font.Font("textures/font/Aladin-Regular.ttf", 36)
        timer_text = font.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
        text_rect = timer_text.get_rect(center=(self.screen.get_width() // 2, 20))
        self.screen.blit(timer_text, text_rect)

    def check_defeat(self):
        """Проверяет столкновение игрока с врагами"""
        player_rect = pygame.Rect(self.player.x, self.player.y, 35, 35)  # Хитбокс игрока

        for enemy in self.enemies:
            enemy_rect = pygame.Rect(enemy.x, enemy.y, 35, 35)  # Хитбокс врага
            if player_rect.colliderect(enemy_rect):  # Проверяем столкновение
                self.game_over(False)  # Вызываем проигрыш
                return

    def check_victory(self):
        """Проверяет, дошёл ли игрок до выхода"""
        player_tile_x = self.player.x // 40
        player_tile_y = self.player.y // 40

        if self.map_data[player_tile_y][player_tile_x] == '2':  # Выход
            self.game_over(True)  # Вызываем победу

    def game_over(self, victory):
        """Завершает уровень (победа или поражение)"""
        if self.is_game_over:  # Если уровень уже завершён, ничего не делаем
            return

        self.is_game_over = True  # Устанавливаем флаг завершения уровня
        self.screen.fill("BLACK")

        if victory:
            self.game.completed_levels.add("Desert")  # Добавляем уровень в пройденные
            with open("data/progress.txt", "r") as file:
                lines = file.readlines()
            if "Desert" not in lines:
                with open("data/progress.txt", "w") as file:
                    file.write("Desert\n")

        # Вычисляем время прохождения
        elapsed_time = int(time.time() - self.start_time)

        font = pygame.font.Font("textures/font/Aladin-Regular.ttf", 48)
        message = "Victory!" if victory else "Defeat!"
        text = font.render(message, True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 3))

        time_font = pygame.font.Font("textures/font/Aladin-Regular.ttf", 42)
        time_text = time_font.render(f"Time: {elapsed_time}", True, (255, 0, 0))
        time_rect = time_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50))

        button_font = pygame.font.Font("textures/font/Aladin-Regular.ttf", 36)
        button_text = button_font.render("OK", True, (255, 0, 0))
        button_rect = pygame.Rect(self.screen.get_width() // 2 - 100, self.screen.get_height() // 2, 200, 100)

        while True:
            self.screen.fill("BLACK")
            self.screen.blit(text, text_rect)
            self.screen.blit(time_text, time_rect)
            pygame.draw.rect(self.screen, (0, 0, 0), button_rect)
            self.screen.blit(button_text, button_text.get_rect(center=button_rect.center))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_rect.collidepoint(event.pos):
                        self.game.current_screen = MainScreen(self.screen, self.game.completed_levels,
                                                              self.game)  # Возвращаемся в меню

                        return  # Выход из экрана завершения


class Game:
    def __init__(self):
        """Инициализация игры"""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("The lost ghost")
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_progress()
        self.current_screen = MainScreen(self.screen, self.completed_levels, self)  # Передаём ссылку на Game

    def start_level(self, level_name):
        """Запуск уровня"""
        if level_name == "Desert":
            self.current_screen = DesertLevel(self.screen, self)

    def load_progress(self):
        """Загрузка прогресса"""
        try:
            with open("data/progress.txt", "r") as file:
                lines = file.readlines()
                self.completed_levels = {line.strip() for line in lines}
        except FileNotFoundError:
            self.completed_levels = set()

    def run(self):
        """Запуск игры"""
        while self.running:
            self.handle_events()
            self.current_screen.update()
            self.clock.tick(60)

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if isinstance(self.current_screen, MainScreen):
                    self.current_screen.handle_click(*event.pos)
            elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if isinstance(self.current_screen, DesertLevel):
                    self.current_screen.handle_events(event)

    def quit(self):
        """Выход из игры"""
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
