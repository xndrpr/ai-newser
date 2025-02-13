import requests
import time
from tabulate import tabulate
import threading
from concurrent.futures import ThreadPoolExecutor
import os
import pandas as pd

url = "http://localhost:1337/v1/chat/completions"

news = """
«Мирный план» Трампа или билет в новую войну?

Судя по всему, Дональд Трамп предлагает сделку, в которой Украина не вернёт оккупированные Россией территории и не вступит в НАТО. Европейским странам придётся самим восстанавливать Украину и обеспечивать её безопасность, а США тем временем готовятся завладеть частью её ресурсов.

Россия не сможет поставить всю Украину под контроль, но и Украина останется без ключевых гарантий безопасности. В итоге проигрывают все — кроме Вашингтона.

Это не мир, а новый «Мюнхен XXI века», предупреждают аналитики. Эр-Рияд (в Саудовской Аравии планируется встреча Путина и Трампа) рискует войти в историю как точка, откуда начнётся новый большой конфликт в Европе. А что думаете вы?

@nexta_live
"""

models = [
    "gpt-4",
    "gpt-4o",
    "gpt-4o-mini",
    "o1",
    "gigachat",
    "llama-3.1-405b",
    "llama-3.3-70b",
    "mixtral-8x7b",
    "phi-4",
    "gemini",
    "gemini-1.5-pro",
    "claude-3-opus",
    "claude-3.5-sonnet",
    "command-r-plus",
    "qwen-2.5-72b",
    "deepseek-v3",
    "deepseek-r1",
    "sonar-pro"
]

results = []
results_lock = threading.Lock()
active_models = set()
active_models_lock = threading.Lock()


def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_status():
    clear_screen()
    print("Currently processing models:")
    with active_models_lock:
        for model in active_models:
            print(f"⏳ {model}")
    print("\nCompleted results:")
    headers = ["Model", "Time (seconds)", "Response Preview"]
    print(tabulate(results, headers=headers, tablefmt="grid"))


def test_model(model):
    # Add model to active set
    with active_models_lock:
        active_models.add(model)
    print_status()

    payload = {
        "model": model,
        "messages": [
            {"role": "system",
                "content": "You are a news analyzer. Read the news and if it's breaking/important, write ONE short breaking news title in Russian (max 10 words). If not important, reply 'Не срочная новость'."},
            {"role": "user", "content": f"News: {news}"}
        ]
    }

    start_time = time.time()
    response = requests.post(url, json=payload, headers={
        "Content-Type": "application/json"})
    end_time = time.time()

    execution_time = round(end_time - start_time, 2)

    with results_lock:
        if "choices" in response.json():
            output = response.json()["choices"][0]["message"]["content"]
            results.append([model, execution_time, output])
        else:
            results.append([model, execution_time, "No response received"])

    # Remove model from active set
    with active_models_lock:
        active_models.remove(model)
    print_status()


# Execute tests in parallel
with ThreadPoolExecutor(max_workers=len(models)) as executor:
    executor.map(test_model, models)

# Final results display
print_status()

# After final results display, save to Excel
df = pd.DataFrame(results, columns=["Model", "Time (seconds)", "Response"])
# Add timestamp to filename to avoid overwriting
timestamp = time.strftime("%Y%m%d-%H%M%S")
excel_filename = f"news_analysis_results_{timestamp}.xlsx"
df.to_excel(excel_filename, index=False)
print(f"\nResults saved to {excel_filename}")
