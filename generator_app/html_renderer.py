# html_renderer.py
from .task_template import AnalyzedTask

class HTMLRenderer:
    # This template is only used for writing a full file, not for the AJAX response.
    template = """
<!DOCTYPE html><html lang="ru"><head><meta charset="UTF-8">
<title>Сгенерированные задачи</title>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
    body {{ font-family: sans-serif; margin: 2em; background-color: #f4f4f9; color: #333; }}
    .task-container {{ background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 1em 1.5em; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }}
    h2, h3 {{ color: #1a1a1a; }}
    details {{ border: 1px solid #eee; border-radius: 4px; margin-top: 10px; }}
    summary {{ cursor: pointer; padding: 10px; font-weight: bold; background-color: #f9f9f9; }}
    .step-content {{ padding: 10px; border-top: 1px solid #eee; }}
</style></head><body><h1>Математические задачи</h1>{task_blocks}</body></html>
"""

    # --- THIS IS THE NEW METHOD YOU NEED TO ADD ---
    def render_single_task_to_html(self, analyzed_task: AnalyzedTask, task_number: int):
        """Renders a single task into an HTML string block."""
        solutions_html = ""
        for question, answer in analyzed_task.solutions.items():
            solutions_html += f"""
            <details>
                <summary>{question}</summary>
                <div class="step-content">{answer}</div>
            </details>
            """
        
        task = analyzed_task.original_task
        task_html_block = f"""
<div class="task-container">
    <h2>Задача {task_number} (Тип: {task.task_type})</h2>
    <div>{task.get_latex_formula()}</div>
    <h3>Вопросы по задаче:</h3>
    {solutions_html}
</div>
"""
        return task_html_block


    # --- YOUR ORIGINAL METHOD FOR WRITING TO A FILE ---
    def render_to_file(self, analyzed_tasks: list, filename="Задачи_с_ответами.html"):
        """Renders a list of tasks into a complete HTML file."""
        all_task_html = ""
        for i, analyzed_task in enumerate(analyzed_tasks, 1):
            # We can reuse the new method here to avoid duplicate code!
            all_task_html += self.render_single_task_to_html(analyzed_task, i)

        final_html = self.template.format(task_blocks=all_task_html)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(final_html)
        print(f"✅ HTML-файл '{filename}' успешно создан. Откройте его в браузере.")