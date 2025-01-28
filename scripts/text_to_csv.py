import re
import sys
from pathlib import Path

from razdel import sentenize

from config import settings


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

    output_path = Path(settings.text_to_csv.DATASET_PATH) / f"{dataset_name}.txt"
    total_sentences = 0

    # Открываем файл для записи один раз перед циклом
    with open(output_path, 'w', encoding='utf-8') as out_file:
        for idx, txt_file in enumerate(txt_files, 1):
            try:
                with open(txt_file, 'r', encoding='utf-8') as in_file:
                    text = in_file.read()

                # Обрабатываем и сразу записываем
                for sentence in process_text(text):
                    out_file.write(sentence + '\n')
                    total_sentences += 1

                # Обновление прогресса
                progress = (idx / total_files) * 100
                sys.stdout.write(
                    f"\rОбработано: {idx}/{total_files} ({progress:.2f}%) | "
                    f"Предложений: {total_sentences}"
                )
                sys.stdout.flush()

            except Exception as e:
                print(f"\nОшибка при обработке файла {txt_file}: {str(e)}")

    print(f"\nИтог: сохранено {total_sentences} предложений в {output_path}")


if __name__ == '__main__':
    main()