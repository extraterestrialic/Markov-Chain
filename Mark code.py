import random
import re
import argparse
import doctest


def read_text_from_file(file_path):
    """Считывает текст из файла (.txt)"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(file_path, "r", encoding="cp1251") as f:
            return f.read()


def tokenize(text):
    """
    Разбивает текст на слова и знаки препинания

    >>> tokenize("Что-то там!")
    ['Что', '-', 'то', 'там', '!']
    >>> tokenize("Это цепь.")
    ['Это', 'цепь', '.']
    """

    return re.findall(r"\w+|[^\w\s]", text)


def build_markov_chain(tokens, order):

    """
    Собирает словарь цепей Маркова

    >>> chain, starts = build_markov_chain(['Это', 'доктест', 'Это', 'доктест'], 1)
    >>> chain
    {('Это',): ['доктест', 'доктест'], ('доктест',): ['Это']}
    >>> starts
    [('Это',), ('Это',)]
    """

    chain = {}
    start_states = []

    for i in range(len(tokens) - order):
        state = tuple(tokens[i : i + order])
        next_token = tokens[i + order]

        if state not in chain:
            chain[state] = []
        chain[state].append(next_token)

        # По условию задачи должно начинаться с заглавной буквы
        first_word = state[0]
        if first_word[0].isupper() and first_word.isalpha():
            start_states.append(state)

    # Если заглавных букв не найдено
    if not start_states and chain:
        start_states = list(chain.keys())

    return chain, start_states


def detokenize(tokens):

    """
    Собирает текст из токенов

    >>> detokenize(['Что-то', 'там', '!'])
    'Что-то там!'
    >>> detokenize(['Это', 'текст', '.'])
    'Это текст.'
    """

    if not tokens:
        return ""

    no_space_before = {".", ",", "!", "?", ";", ":", ")", "]", "}", "%", "»"}
    no_space_after = {"(", "[", "{", "«"}

    result = []
    in_quote = False

    for i, token in enumerate(tokens):
        if i == 0:
            result.append(token)
            if token == '"':
                in_quote = True
            continue

        if token == '"':
            if in_quote:
                result.append(token)
                in_quote = False
            else:
                result.append(" " + token)
                in_quote = True
            continue

        if (
            token in no_space_before
            or tokens[i - 1] in no_space_after
            or (in_quote and tokens[i - 1] == '"')
        ):
            result.append(token)
        else:
            result.append(" " + token)

    return "".join(result)


def generate_text(chain, start_states, order, target_words):
    """
        Генерирует текст

        >>> import random
        >>> random.seed(42) # Фиксируем случайность для теста
        >>> my_chain = {('Это',): ['доктест'], ('доктест',): ['!']}
        >>> generate_text(my_chain, [('Это',)], 1, 2)
        'Это доктест'
    """

    if not chain or target_words <= 0:
        return ""

    current_state = random.choice(start_states)
    result_tokens = list(current_state)

    words_count = sum(1 for token in result_tokens if token.isalpha())

    while words_count < target_words:
        # Если слово встретилось единожды и было последним
        if current_state not in chain or not chain[current_state]:
            current_state = random.choice(start_states)
            if result_tokens and result_tokens[-1] not in {".", "!", "?"}:
                result_tokens.append(".")
            result_tokens.extend(current_state)
            words_count += sum(1 for token in current_state if token.isalpha())
            continue

        next_token = random.choice(chain[current_state])
        result_tokens.append(next_token)

        if next_token.isalpha():
            words_count += 1

        current_state = tuple(result_tokens[-order:])

    return detokenize(result_tokens)


def main():
    print("==================================================")
    print("      ГЕНЕРАТОР ТЕКСТА НА ЦЕПЯХ МАРКОВА          ")
    print("==================================================\n")

    # 1.парсер читает командную строку. nargs+ файлов может быть много

    parser = argparse.ArgumentParser(description="Генератор текста на цепях Маркова")
    parser.add_argument("files", nargs="+", help="Пути к файлам .txt")
    parser.add_argument("--order", type=int, default=2, help="Порядок цепи")
    parser.add_argument("--length", type=int, default=50, help="Количество слов")
    parser.add_argument("--seed", type=int, default=None, help="Сид для генератора")

    # nargs+ файлов может быть много

    # считываем что ввел пользователь
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # заменили кусок с вводом порядка,длины и файлов вместо громоздких циклов через args

    file_paths = args.files
    order = args.order
    target_words = args.length


    # заменили кусок с вводом порядка через args

    all_texts = []
    for file_path in file_paths:
        try:
            text = read_text_from_file(file_path)
            if text.strip():
                all_texts.append(text)
        except FileNotFoundError:
            print(f"[Ошибка]: Файл '{file_path}' не найден.")

    if not all_texts:
        print("Ошибка: не удалось прочитать ни одного файла.")
        return

    full_corpus = "\n\n".join(all_texts)
    tokens = tokenize(full_corpus)

    if len(tokens) <= order:
        print("Текст слишком короткий для такого порядка цепи!")
        return

    chain, start_states = build_markov_chain(tokens, order)

    print(f"\nЧтение файлов завершено ({len(file_paths)} шт.).")
    print(f"Обучение завершено! Всего уникальных состояний: {len(chain)}\n")
    print("--- Сгенерированный текст ---")

    result = generate_text(chain, start_states, order, target_words)
    print(result)


if __name__ == "__main__":

    doctest.testmod()  # запускает все тесты в файле

    main()
