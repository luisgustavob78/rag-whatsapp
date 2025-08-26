def save_txt_file(file_path, text):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


def load_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
