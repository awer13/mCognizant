# main.py
import random
from core import TaskController # Ваше ядро из предыдущих шагов
from task_template import SeriesTaskClass1, SeriesTaskClass2
from analyzer import TaskAnalyzer
from html_renderer import HTMLRenderer

# --- Генераторы ---
class SeriesGeneratorClass1:
    def generate(self):
        c = random.randint(3, 12); b = random.randint(-(c - 1), c - 1)
        if b == 0: b = 1
        return SeriesTaskClass1(b=b, c=c, n_for_an=random.randint(3, 7), n_for_sn=random.randint(7, 12))

class SeriesGeneratorClass2:
    def generate(self):
        c = random.randint(1, 10) if random.choice([True, False]) else random.randint(-12, -3)
        return SeriesTaskClass2(c=c, n_for_an=random.randint(2, 5), n_for_sn=random.randint(7, 12))

# --- Основной скрипт ---
if __name__ == "__main__":
    # 1. Инициализация всех компонентов
    controller = TaskController()
    analyzer = TaskAnalyzer()
    renderer = HTMLRenderer()

    # 2. Регистрация генераторов
    controller.register_generator('series_class_1', SeriesGeneratorClass1)
    controller.register_generator('series_class_2', SeriesGeneratorClass2)

    # 3. Генерация "сырых" задач
    tasks = [controller.create_task('series_class_1'), controller.create_task('series_class_2')]

    # 4. Анализ каждой задачи для получения ответов и шагов
    analyzed_tasks = [analyzer.analyze(task) for task in tasks if task]

    # 5. Рендеринг финального HTML-файла
    if analyzed_tasks:
        renderer.render_to_file(analyzed_tasks)