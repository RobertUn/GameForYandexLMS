import pygame


class MainScreen:
    def __init__(self, screen, completed_levels):
        """Инициализация главного экрана"""
        self.screen = screen
        self.completed_levels = completed_levels
        self.background_layers = [
            pygame.image.load("textures/background/BG1.png", ).convert_alpha(),
            pygame.image.load("textures/background/BG2.png").convert_alpha(),
            pygame.image.load("textures/background/BG3.png").convert_alpha()
        ]
        self.font_small = pygame.font.Font("textures/font/Aladin-Regular.ttf", 30)  # Маленький шрифт
        self.font_large = pygame.font.Font("textures/font/Aladin-Regular.ttf", 60)  # Большой шрифт
        print(completed_levels)
    def draw(self):
        """Отрисовка всех слоев фона"""
        for layer in self.background_layers:
            layer = pygame.transform.scale(layer, (800, 600))
            self.screen.blit(layer, (0, 0))

        # Верхний левый угол (белый текст)
        text_top = self.font_small.render("Developer: UnRobWarrior", True, (255, 255, 255))
        self.screen.blit(text_top, (10, 10))

        # Заголовок в центре
        text_title = self.font_large.render("The lost ghost", True, (255, 255, 255))
        text_rect = text_title.get_rect(center=(400, 200))  # Центрируем по горизонтали
        self.screen.blit(text_title, text_rect)

        # Кнопки
        button_texts = ["Desert", "Ocean", "Hell"]
        for i, text in enumerate(button_texts):
            color = (100, 100, 100)
            if text in self.completed_levels or text == "Desert":
                color = (255, 255, 255)
            button = self.font_small.render(text, True, color)
            button_rect = button.get_rect(center=(400, 300 + i * 50))  # Размещение кнопок
            self.screen.blit(button, button_rect)

    def update(self):
        """Обновление экрана"""
        self.draw()
        pygame.display.flip()


class Game:
    def __init__(self):
        """Инициализация игры"""
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))  # Размер окна
        pygame.display.set_caption("The lost ghost")
        self.clock = pygame.time.Clock()
        self.running = True
        self.load_progress()
        self.main_screen = MainScreen(self.screen, self.completed_levels)

    def load_progress(self):
        """Загрузка прогресса из файла"""
        try:
            with open("data/progress.txt", "r") as file:
                lines = file.readlines()
                self.completed_levels = {line.strip() for line in lines}  # Сет пройденных уровней
        except FileNotFoundError:
            self.completed_levels = set()  # Если файла нет, ни один уровень не пройден

    def run(self):
        """Запуск игрового цикла"""
        while self.running:
            self.handle_events()
            self.main_screen.update()
            self.clock.tick(60)

    def handle_events(self):
        """Обработка событий"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 350 < x < 450:
                    if 285 < y < 315:
                        print("Desert")
                    elif 335 < y < 365 and "Ocean" in self.completed_levels:
                        print("Ocean")
                    elif 385 < y < 415 and "Hell" in self.completed_levels:
                        print("Hell")

    def quit(self):
        """Выход из игры"""
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
