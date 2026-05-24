import json
import time
import requests
import os
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    drinks_file_path = os.path.join(script_dir, 'drinks_details.json')
    ingredients_file_path = os.path.join(script_dir, 'ingredients.json')
    
    if not os.path.exists(drinks_file_path):
        print(f"Файл {drinks_file_path} не знайдено.")
        return

    print("Читання файлу drinks_details.json...")
    with open(drinks_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    drinks = data.get("drinks", [])
    
    # Використовуємо словник для уникнення дублікатів через різний регістр букв (напр. "Vodka" і "vodka")
    unique_ingredients_dict = {}

    for drink in drinks:
        for i in range(1, 16):
            ingredient_key = f"strIngredient{i}"
            ingredient = drink.get(ingredient_key)
            if ingredient and isinstance(ingredient, str):
                ingredient = ingredient.strip()
                if ingredient:
                    key = ingredient.lower()
                    if key not in unique_ingredients_dict:
                        unique_ingredients_dict[key] = ingredient

    ingredients_list = sorted(list(unique_ingredients_dict.values()))
    print(f"Знайдено {len(ingredients_list)} унікальних інгредієнтів. Починаємо завантаження даних...")

    api_search_url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?i={}"
    ingredients_details_list = []

    for idx, ingredient in enumerate(ingredients_list):
        print(f"Завантаження даних для інгредієнта '{ingredient}' ({idx + 1}/{len(ingredients_list)})...")
        
        try:
            resp = requests.get(api_search_url.format(ingredient))
            resp.raise_for_status()
            
            # Якщо API повертає не JSON (наприклад помилку 404), це викине exception, який ми спіймаємо нижче
            ingredient_data = resp.json()
            
            if ingredient_data and "ingredients" in ingredient_data and ingredient_data["ingredients"]:
                # Беремо перший знайдений результат
                ingredients_details_list.append(ingredient_data["ingredients"][0])
            else:
                print(f"Попередження: Не знайдено даних для інгредієнта '{ingredient}' в API")
                
        except Exception as e:
            print(f"Помилка при завантаженні даних для інгредієнта '{ingredient}': {e}")
            
        # Невелика затримка, щоб не перевантажувати сервер
        time.sleep(0.1)

    print("\nЗбереження даних у JSON файл...")
    with open(ingredients_file_path, 'w', encoding='utf-8') as f:
        json.dump({"ingredients": ingredients_details_list}, f, ensure_ascii=False, indent=2)

    print(f"Готово! Файл успішно створено:\n- {ingredients_file_path}")

if __name__ == "__main__":
    main()
