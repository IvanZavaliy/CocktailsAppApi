import requests
from bs4 import BeautifulSoup
import json
import time
import string
import os

def main():
    # Будемо перебирати літери a-z та цифри 0-9
    letters = string.ascii_lowercase + "0123456789"
    base_browse_url = "https://www.thecocktaildb.com/browse/letter/{}"
    api_lookup_url = "https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={}"

    all_ids = []

    print("Починаємо збір ID коктейлів...")
    for letter in letters:
        url = base_browse_url.format(letter)
        print(f"Обробка сторінки: {url}")
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Помилка при завантаженні {url}: {e}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Знаходимо всі div з класом col-sm-3
        divs = soup.find_all('div', class_='col-sm-3')
        
        for div in divs:
            a_tag = div.find('a')
            if a_tag and 'href' in a_tag.attrs:
                href = a_tag['href']
                # Приклад href: /drink/14364 або /drink/14364-Drink-Name
                if '/drink/' in href:
                    parts = href.split('/')
                    if len(parts) >= 3:
                        drink_id_raw = parts[2]
                        
                        # Відкидаємо можливі додатки у посиланні (наприклад, -Drink-Name)
                        drink_id = drink_id_raw.split('-')[0]
                        
                        if drink_id.isdigit() and drink_id not in all_ids:
                            all_ids.append(drink_id)
        
        # Невелика затримка, щоб не перевантажувати сервер
        time.sleep(0.5)

    print(f"\nЗнайдено {len(all_ids)} унікальних ID коктейлів.")
    
    if not all_ids:
        print("Коктейлів не знайдено, завершення програми.")
        return

    print("Починаємо завантаження деталей за кожним ID...")

    drinks_details_list = []
    drinks_short_list = []

    for idx, drink_id in enumerate(all_ids):
        print(f"Завантаження даних для коктейлю {drink_id} ({idx + 1}/{len(all_ids)})...")
        lookup_url = api_lookup_url.format(drink_id)
        
        try:
            resp = requests.get(lookup_url)
            resp.raise_for_status()
            data = resp.json()
            
            if data and "drinks" in data and data["drinks"]:
                drink_info = data["drinks"][0]
                
                # Додаємо повну інформацію
                drinks_details_list.append(drink_info)
                
                # Додаємо коротку інформацію
                short_info = {
                    "idDrink": drink_info.get("idDrink"),
                    "strDrink": drink_info.get("strDrink"),
                    "strDrinkThumb": drink_info.get("strDrinkThumb")
                }
                drinks_short_list.append(short_info)
                
        except Exception as e:
            print(f"Помилка при завантаженні даних для ID {drink_id}: {e}")
            
        # Невелика затримка для API, щоб не отримати бан
        time.sleep(0.1)

    # Збереження результатів у JSON в поточній директорії, де запущено скрипт
    print("\nЗбереження даних у JSON файли...")
    
    # Визначаємо шлях до директорії скрипта
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    details_path = os.path.join(script_dir, 'drinks_details.json')
    short_path = os.path.join(script_dir, 'drinks.json')
    
    with open(details_path, 'w', encoding='utf-8') as f:
        json.dump({"drinks": drinks_details_list}, f, ensure_ascii=False, indent=2)
        
    with open(short_path, 'w', encoding='utf-8') as f:
        json.dump({"drinks": drinks_short_list}, f, ensure_ascii=False, indent=2)

    print(f"Готово!\nФайли успішно створено:\n- {details_path}\n- {short_path}")

if __name__ == "__main__":
    main()
