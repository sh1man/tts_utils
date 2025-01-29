import re
import sys
from pathlib import Path

from razdel import sentenize

from config import settings
from scripts.utils import MemoryBuffer


def process_text(text):
    cleaned = re.sub(r'\(.*?\)|<.*?>|["«»„“•*:$]|[\[\]]|(\b\d+\.\s*)', '', text)
    cleaned = re.sub(r'\b[А-ЯA-Z]\W+', '', cleaned, flags=re.IGNORECASE)
    # Нормализация пробелов перед пунктуацией
    cleaned = re.sub(r'\s+([.,!?])', r'\1', cleaned)
    cleaned = re.sub(r'/', 'или', cleaned)
    cleaned = re.sub(r'№', 'номер', cleaned)
    # Заменяет любые последовательности пробельных символов (даже очень длинные) на один обычный пробел
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    cleaned = re.sub(r';.', '.', cleaned)
    cleaned = re.sub(r'=', '.', cleaned)
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
    print("Введите название датасета (ресурс+контекст данных) например:")
    print("Arzamas это ресурс с которого взяли инфу а конткекст данных у него культурно-исторические артефакты и их современные интерпретации")
    print("И назвали его ArzamasCAAC")
    sys.stdout.write("Введите название: ")
    dataset_name = input().strip()

    txt_files = list(Path(settings.text_to_csv.DATASET_PATH).glob('**/*.txt'))
    total_files = len(txt_files)
    buffer = MemoryBuffer(max_size_gb=2)
    part_number = 1
    total_sentences = 0

    try:
        for idx, txt_file in enumerate(txt_files, 1):
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()

            for sentence in process_text(text):
                if not buffer.add(sentence):
                    # Записываем буфер в файл
                    output_path = Path(settings.text_to_csv.DATASET_PATH) / f"{dataset_name}_part{part_number}.txt"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(buffer.buffer))

                    part_number += 1
                    buffer.clear()
                    buffer.add(sentence)  # Добавляем текущее предложение в новый буфер

                total_sentences += 1

            # Прогресс
            progress = (idx / total_files) * 100
            sys.stdout.write(
                f"\rОбработано: {idx}/{total_files} ({progress:.2f}%) | "
                f"Текущий буфер: {buffer.current_size / 1024 ** 3:.2f} ГБ | "
                f"Частей: {part_number}"
            )
            sys.stdout.flush()

        # Запись остатка
        if buffer.current_size > 0:
            output_path = Path(settings.text_to_csv.DATASET_PATH) / f"{dataset_name}_part{part_number}.txt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(buffer.buffer))

    except MemoryError:
        print("\nОШИБКА: Недостаточно памяти! Уменьшите размер буфера.")
        sys.exit(1)

    print(f"\nИтог: {total_sentences} предложений сохранено в {part_number} файлах")


if __name__ == '__main__':
    main()