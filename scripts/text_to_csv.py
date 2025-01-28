import re
import sys
from pathlib import Path

from razdel import sentenize

from config import settings


def process_text(text):
    cleaned = re.sub(r'\(.*?\)|<.*?>|["«»„“•*:]|[\[\]]|(\b\d+\.\s*)', '', text)
    cleaned = re.sub(r'\b[А-ЯA-Z]\W+', '', cleaned, flags=re.IGNORECASE)
    # Нормализация пробелов перед пунктуацией
    cleaned = re.sub(r'\s+([.,!?])', r'\1', cleaned)
    cleaned = re.sub(r'/', 'или', cleaned)
    cleaned = re.sub(r'№', 'номер', cleaned)
    # Заменяет любые последовательности пробельных символов (даже очень длинные) на один обычный пробел
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r';.', '.', cleaned)
    # Разделяем на предложения
    sentences = [s.text for s in sentenize(cleaned)]

    # Постобработка
    processed = []
    for sent in sentences:
        # Пропускаем предложения с английскими буквами
        if re.search(r'[A-Za-z]', sent):
            continue

        # Пропускаем предложения с цифрой перед буквой (например: 1Свинец, 2Яшма)
        if re.search(r'\d[А-Яа-я]', sent):
            continue
        # Убираем лишние точки в начале
        sent = re.sub(r'^[.,]+', '', sent)

        # Фикс пробелов в конце
        sent = re.sub(r'\s+([.!?])$', r'\1', sent)
        for item in sent.split('.'):
            # Удаляем начальные небуквенные символы (кроме '-'), а также записи вида "А.", "М.,", "М.."
            item = re.sub(r'^[^\w-]+|(?<!\w)[А-ЯA-Z]\W+', '', item, flags=re.IGNORECASE)
            item = item.strip()
            # Добавляем точку в конце предложения если отсутствует
            if item and not re.search(r'[.!?…]$', item):
                item += '.'
            # Капитализация первой буквы
            if item:
                item = item[0].upper() + item[1:]

            processed.append(item)

    return [s for s in processed if s]


def main():
    print("Введите название датасета (контекст данных+ресурс) например:")
    print("Arzamas это ресурс с которого взяли инфу а конткекст данных у него культурно-исторические артефакты и их современные интерпретации")
    print("И назвали его ArzamasCAAC")
    sys.stdout.write("Введите название: ")
    dataset_name = input()
    txt_files = list(Path(settings.text_to_csv.DATASET_PATH).glob('**/*.txt'))
    total_files = len(txt_files)
    processed_files = 0
    all_sentences = []
    for txt_file in txt_files:
        with open(txt_file, 'r', encoding='utf-8') as f:
            text = f.read()
            processed = process_text(text)
            all_sentences.extend(processed)

        # Обновляем прогресс
        processed_files += 1
        remaining = total_files - processed_files
        progress = (processed_files / total_files) * 100 if total_files > 0 else 0

        sys.stdout.write(
            f"\rОбработано файлов: {processed_files}/{total_files} "
            f"({progress:.2f}%) | Осталось: {remaining}"
        )
        sys.stdout.flush()

        # Сохранение в текстовый файл
    output_path = Path(settings.text_to_csv.DATASET_PATH) / f"{dataset_name}.txt"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(all_sentences))

    print(f"\nСохранено {len(all_sentences)} предложений в {output_path}")


if __name__ == '__main__':
    main()
