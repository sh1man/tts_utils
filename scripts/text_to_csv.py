import re
import sys
from pathlib import Path

from razdel import sentenize

from config import settings


def process_text(text):
    cleaned = re.sub(r'\(.*?\)|<.*?>|["«»„“]|[\[\]]', '', text)
    # Нормализация пробелов перед пунктуацией
    cleaned = re.sub(r'\s+([.,!?])', r'\1', cleaned)
    # Заменяет любые последовательности пробельных символов (даже очень длинные) на один обычный пробел
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    # Разделяем на предложения
    sentences = [s.text for s in sentenize(cleaned)]

    # Постобработка
    processed = []
    for sent in sentences:
        # Пропускаем предложения с английскими буквами
        if re.search(r'[A-Za-z]', sent):
            continue

        # Убираем лишние точки в начале
        sent = re.sub(r'^[.,]+', '', sent)

        # Фикс пробелов в конце
        sent = re.sub(r'\s+([.!?])$', r'\1', sent)
        # Добавляем точку в конце предложения если отсутствует
        if sent and not re.search(r'[.!?…]$', sent):
            sent += '.'
        # Капитализация первой буквы
        if sent:
            sent = sent[0].upper() + sent[1:]
        processed.append(sent)

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
