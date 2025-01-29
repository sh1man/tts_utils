import json
import os
from pathlib import Path

from config import get_config


class Phonemizer:
    def __init__(self):
        from ruaccent import RUAccent
        from ruphon import RUPhon
        phonemizer = RUPhon()
        self.phonemizer = phonemizer.load("big", workdir="./models", device="cuda")
        self.accentizer = RUAccent()
        self.accentizer.load(omograph_model_size='turbo3', use_dictionary=True, tiny_mode=False)

    def get_phonetic_transcription(self, text: str) -> str:
        """
        Возвращает фонетическую транскрипцию для заданного фрагмента текста.
        """
        accented_text = self.accentizer.process_all(text)
        return self.phonemizer.phonemize(accented_text, put_stress=True, stress_symbol="'")


    def split_text_by_limit(self, text: str, limit: int) -> list[str]:
        """
        Splits the text into fragments of maximum `limit` characters,
        trying to “break” the fragment at the last point ('.') before the limit.
        """
        fragments = []
        start_index = 0
        text_len = len(text)

        while start_index < text_len:
            end_index = min(start_index + limit, text_len)
            last_period_index = text.rfind('.', start_index, end_index)

            if last_period_index == -1:
                chunk = text[start_index:end_index]
                start_index = end_index
            else:
                chunk = text[start_index:last_period_index + 1]
                start_index = last_period_index + 1

            fragments.append(chunk.strip())

        return fragments


    def run(self):
        config = get_config()
        dataset_path: Path = config.text_to_json.DATASET_PATH
        split_characters: int = config.text_to_json.SPLIT_CHARACTERS
        print(dataset_path)
        for root, dirs, files in os.walk(dataset_path):
            for file_name in files:
                if file_name.endswith('.txt'):
                    txt_file_path = Path(root) / file_name

                    with open(txt_file_path, 'r', encoding='utf-8') as f:
                        text = f.read()

                    raw_fragments = self.split_text_by_limit(text, split_characters)

                    segments = []
                    for frag in raw_fragments:
                        segments.append({
                            "text": frag,
                            "phonetic": self.get_phonetic_transcription(frag)
                        })

                    data_for_json = {
                        "segments": segments,
                        "chars": len(text)
                    }

                    json_file_path = txt_file_path.with_suffix('.json')
                    with open(json_file_path, 'w', encoding='utf-8') as jf:
                        json.dump(data_for_json, jf, ensure_ascii=False, indent=2)

                    print(f"Saved: {json_file_path}")


if __name__ == '__main__':
    print("text")
