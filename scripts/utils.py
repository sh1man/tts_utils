class MemoryBuffer:
    def __init__(self, max_size_gb=2):
        self.buffer = []
        self.max_size = max_size_gb * 1024 ** 3  # 2 ГБ в байтах
        self.current_size = 0

    def add(self, sentence):
        sentence_bytes = (sentence + '\n').encode('utf-8')
        sentence_size = len(sentence_bytes)

        if self.current_size + sentence_size > self.max_size:
            return False  # Не хватает места

        self.buffer.append(sentence)
        self.current_size += sentence_size
        return True

    def clear(self):
        self.buffer = []
        self.current_size = 0
