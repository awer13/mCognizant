# generator_app/views.py

import json
import traceback
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .core import TaskController
from .analyzer import TaskAnalyzer
from .html_renderer import HTMLRenderer
from .generators.series_generator_1 import SeriesGeneratorClass1
from .generators.series_generator_2 import SeriesGeneratorClass2
from .generators.series_generator_3 import SeriesGeneratorClass3
from .generators.series_generator_4 import SeriesGeneratorClass4

from django.views.decorators.csrf import ensure_csrf_cookie


controller = TaskController()
analyzer = TaskAnalyzer()
renderer = HTMLRenderer()


controller.register_generator('series_class_1', SeriesGeneratorClass1)
controller.register_generator('series_class_2', SeriesGeneratorClass2)
controller.register_generator('series_class_3', SeriesGeneratorClass3)
controller.register_generator('series_class_4', SeriesGeneratorClass4)


@ensure_csrf_cookie
def index_view(request):
    """Рендерит главную HTML-страницу."""
    return render(request, 'generator_app/index.html')

class GenerateTaskView(View):
    """Обрабатывает AJAX-запрос на генерацию задачи."""
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            task_type = data.get('task_type')
            
            # В ТЗ для новых задач нет параметра сложности, но мы можем его оставить
            complexity = int(data.get('complexity', 10))

            # Логика создания и анализа задачи остается неизменной
            task = controller.create_task(task_type, complexity=complexity)
            if not task:
                return JsonResponse({'error': 'Task creation failed'}, status=400)
            
            analyzed_task = analyzer.analyze(task)
            
            task_html = renderer.render_single_task_to_html(analyzed_task, 1)

            return JsonResponse({'html': task_html})
            
        except Exception as e:
            print("--- AN ERROR OCCURRED ---")
            traceback.print_exc() 
            print("--------------------------")
            return JsonResponse({'error': 'An error occurred, check server logs.'}, status=500)