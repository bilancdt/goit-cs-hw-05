import string
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import matplotlib.pyplot as plt

def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

# Видалення пунктуації
def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))

# Map-функція: повертає пару (слово, 1)
def map_function(word):
    return word, 1

# Shuffle-функція: групує слова з однаковими ключами
def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()

# Reduce-функція: підсумовує значення для кожного слова
def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)

# Основна функція MapReduce
def map_reduce(text, search_words=None):
    # Видалення пунктуації та розбиття тексту на слова
    text = remove_punctuation(text)
    words = text.lower().split()

    # Якщо задано список пошукових слів, враховуємо тільки їх
    if search_words:
        words = [word for word in words if word in search_words]

    # Паралельний Map
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельний Reduce
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)

# Функція для візуалізації результатів
def visualize_top_words(word_counts, top_n=10):

    sorted_word_counts = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    words, counts = zip(*sorted_word_counts)

    plt.figure(figsize=(10, 6))
    plt.bar(words, counts, color='skyblue')
    plt.xlabel("Слова")
    plt.ylabel("Частота")
    plt.title(f"Топ-{top_n} найчастіше вживаних слів")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    url = "https://www.gutenberg.org/files/1342/1342-0.txt"  
    text = get_text(url)

    if text:
        # Виконання MapReduce з пошуковими словами
        search_words = None  # Можна задати список пошукових слів, наприклад: ['pride', 'prejudice', 'love', 'marriage', 'happiness','peace']
        result = map_reduce(text, search_words)

        print("Результат підрахунку слів:")
        for word, count in sorted(result.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"{word}: {count}")

        # Візуалізація 
        visualize_top_words(result, top_n=10)
    else:
        print("Помилка: Не вдалося завантажити текст.")
