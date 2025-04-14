# hamming_coder.py
import math
import os # Для перевірки існування файлу

# --- Допоміжні функції для параметрів коду Хемінга ---

def calculate_hamming_params(m):
    """Розраховує кількість контрольних бітів (k) та загальну довжину (n)
    для m інформаційних бітів."""
    k = 0
    # Формула Хемінга: 2^k >= m + k + 1
    while 2**k < m + k + 1:
        k += 1
    n = m + k
    return k, n

def get_check_bit_positions(n):
    """Повертає список позицій контрольних бітів (1, 2, 4, 8...)."""
    positions = []
    i = 0
    while True:
        pos = 2**i
        if pos <= n:
            positions.append(pos)
            i += 1
        else:
            break
    return positions

def get_data_bit_positions(n):
    """Повертає список позицій інформаційних бітів."""
    check_positions = get_check_bit_positions(n)
    all_positions = list(range(1, n + 1))
    data_positions = [pos for pos in all_positions if pos not in check_positions]
    return data_positions

# --- Encoding Functions ---

def calculate_check_bits(data_bits_str, m, k, n):
    """Розраховує значення контрольних бітів для заданого блоку даних (рядок '0' та '1')."""
    check_positions = get_check_bit_positions(n)
    data_positions = get_data_bit_positions(n)

    # Створюємо словник для кодового слова {позиція: значення_біта}
    code_word = {}
    data_bit_index = 0
    for pos in range(1, n + 1):
        if pos in data_positions:
            # Беремо біт з вхідного рядка
            if data_bit_index < len(data_bits_str):
                code_word[pos] = int(data_bits_str[data_bit_index])
            else:
                 # Якщо даних менше ніж m (останній блок), доповнюємо нулями
                 code_word[pos] = 0
            data_bit_index += 1
        else:
            # Залишаємо місце для контрольних бітів (поки що 0)
            code_word[pos] = 0

    # Розраховуємо кожен контрольний біт
    calculated_check_bits = {}
    for p_pos in check_positions:
        parity_sum = 0
        # Перебираємо всі позиції, щоб знайти ті, які контролює p_pos
        for bit_pos in range(1, n + 1):
            # Контрольний біт не контролює сам себе для розрахунку
            # і контролює позицію, якщо p_pos є в двійковому розкладі біт_pos
            # (перевірка через побітове AND)
            if bit_pos != p_pos and (bit_pos & p_pos) != 0:
                parity_sum += code_word.get(bit_pos, 0) # Додаємо значення біта на цій позиції

        # Правило парності (even parity): якщо сума непарна, контрольний біт = 1
        calculated_check_bits[p_pos] = parity_sum % 2

    return calculated_check_bits

def encode_block(data_block_str, m):
    """Кодує один блок інформаційних бітів (рядок '0' та '1') кодом Хемінга."""
    k, n = calculate_hamming_params(m)
    check_positions = get_check_bit_positions(n)
    data_positions = get_data_bit_positions(n)

    # Розраховуємо значення контрольних бітів
    check_bit_values = calculate_check_bits(data_block_str, m, k, n)

    # Формуємо повне кодове слово (список рядків '0' або '1')
    encoded_list = []
    data_bit_index = 0
    for pos in range(1, n + 1):
        if pos in check_positions:
            encoded_list.append(str(check_bit_values[pos]))
        else:
            # Додаємо інформаційний біт
            if data_bit_index < len(data_block_str):
                 encoded_list.append(data_block_str[data_bit_index])
            else:
                 # Доповнення нулями, якщо блок неповний
                 encoded_list.append('0')
            data_bit_index += 1

    # Повертаємо рядок '0'/'1' довжиною n
    return "".join(encoded_list)

def encode_file(input_filepath, output_filepath, m):
    """Кодує текстовий файл за методом Хемінга."""
    print(f"Кодування файлу '{input_filepath}' у '{output_filepath}' з m={m}...")
    k, n = calculate_hamming_params(m)
    print(f"Параметри коду: k={k}, n={n}")

    try:
        # Читаємо вхідний файл як байти ('rb')
        # Записуємо вихідний файл як текст ('w') для збереження '0' та '1'
        with open(input_filepath, 'rb') as infile, open(output_filepath, 'w') as outfile:
            bit_buffer = ""
            encoded_block_count = 0
            while True:
                byte_read = infile.read(1) # Читаємо один байт
                if not byte_read:
                    break # Кінець файлу

                # Перетворюємо байт в 8-бітний рядок (з доповненням нулями зліва)
                bit_buffer += format(byte_read[0], '08b')

                # Поки в буфері є достатньо біт для повного інформаційного блоку
                while len(bit_buffer) >= m:
                    data_block = bit_buffer[:m] # Беремо m біт
                    bit_buffer = bit_buffer[m:]      # Залишаємо решту в буфері
                    encoded_block_str = encode_block(data_block, m)
                    outfile.write(encoded_block_str) # Записуємо n біт ('0'/'1')
                    encoded_block_count += 1

            # Обробка залишку бітів у буфері (якщо він є)
            if bit_buffer:
                print(f"Залишилось {len(bit_buffer)} біт в буфері. Обробка останнього блоку...")
                # Важливо: Ми доповнюємо останній блок нулями до m біт.
                actual_last_block_len = len(bit_buffer)
                padding_len = m - actual_last_block_len
                data_block = bit_buffer + '0' * padding_len
                print(f"Доповнено {padding_len} нулями до m={m}.")

                encoded_block_str = encode_block(data_block, m)
                outfile.write(encoded_block_str)
                encoded_block_count += 1
                # Записуємо інформацію про доповнення (наприклад, в окремий файл або на початок)

        print(f"Файл '{input_filepath}' успішно закодовано у '{output_filepath}'.")
        print(f"Всього оброблено блоків: {encoded_block_count}")

    except FileNotFoundError:
        print(f"Помилка: Вхідний файл '{input_filepath}' не знайдено.")
    except Exception as e:
        print(f"Сталася помилка під час кодування: {e}")


# --- Decoding Functions ---

def decode_block(encoded_block_str, m):
    """Декодує та виправляє (якщо можливо) один блок Хемінга (рядок '0'/'1').
       Повертає рядок інформаційних бітів."""
    k, n = calculate_hamming_params(m)
    if len(encoded_block_str) != n:
        # Це може бути останній неповний блок при читанні, якщо щось пішло не так
        print(f"Помилка: Очікувана довжина блоку {n}, отримано {len(encoded_block_str)}. Блок пропущено.")
        return None # Повертаємо None, щоб позначити помилку

    check_positions = get_check_bit_positions(n)
    data_positions = get_data_bit_positions(n)

    # Перетворюємо отриманий рядок у словник {позиція: значення}
    received_code_word = {}
    for i, bit_char in enumerate(encoded_block_str):
         received_code_word[i + 1] = int(bit_char) # Позиції 1..n

    # Розраховуємо синдром помилки
    syndrome = 0
    for p_pos in check_positions:
        parity_sum = 0
        # Перебираємо всі позиції, які контролює p_pos
        for bit_pos in range(1, n + 1):
            if bit_pos != p_pos and (bit_pos & p_pos) != 0:
                parity_sum += received_code_word.get(bit_pos, 0)

        # Розрахований контрольний біт для отриманих даних
        calculated_check_bit = parity_sum % 2
        # Контрольний біт, який ми отримали у блоці
        received_check_bit = received_code_word.get(p_pos, 0)

        # Якщо вони не збігаються, додаємо позицію контрольного біта до синдрому
        if calculated_check_bit != received_check_bit:
            syndrome += p_pos

    # Виправлення помилки, якщо вона виявлена і є одиночною
    if syndrome > 0:
        if syndrome <= n:
            print(f"  -> Знайдено помилку в блоці на позиції {syndrome}. Виправлення...")
            # Інвертуємо біт на позиції синдрому
            received_code_word[syndrome] = 1 - received_code_word[syndrome]
        else:
             # Синдром вказує на позицію за межами блоку - це неможливо для одиночної помилки
             print(f"  -> Помилка! Синдром {syndrome} виходить за межі блоку {n}. Можливо, множинна помилка. Виправлення неможливе.")
             # В цьому випадку ми не виправляємо, повернемо дані як є (з помилками)

    # Витягнення інформаційних бітів з (можливо, виправленого) слова
    decoded_bits_list = []
    for pos in data_positions:
         # Переконуємось, що позиція існує (на випадок помилок)
         if pos in received_code_word:
            decoded_bits_list.append(str(received_code_word[pos]))

    # Повертаємо рядок з m інформаційними бітами
    # Важливо: функція повертає m біт, навіть якщо останній блок був доповнений.
    # Логіка відкидання зайвих бітів має бути у функції декодування файлу.
    return "".join(decoded_bits_list[:m])


def decode_file(input_filepath, output_filepath, m):
    """Декодує файл, закодований методом Хемінга."""
    print(f"Декодування файлу '{input_filepath}' у '{output_filepath}' з m={m}...")
    k, n = calculate_hamming_params(m)
    print(f"Параметри коду: k={k}, n={n}")

    try:
        # Читаємо закодований файл як текст ('r')
        # Записуємо відновлений файл як байти ('wb')
        with open(input_filepath, 'r') as infile, open(output_filepath, 'wb') as outfile:
            bit_buffer = ""
            decoded_block_count = 0
            while True:
                # Читаємо n символів ('0' або '1') з файлу
                encoded_block_str = infile.read(n)
                if not encoded_block_str:
                    break # Кінець файлу

                # Перевірка, чи отримали повний блок
                if len(encoded_block_str) < n:
                     print(f"Попередження: Останній прочитаний блок неповний ({len(encoded_block_str)} біт замість {n}). Можливо, досягнуто кінця файлу або файл пошкоджено.")
                     # Пропускаємо неповний блок
                     break

                print(f"Обробка блоку {decoded_block_count + 1}...")
                decoded_data_bits = decode_block(encoded_block_str, m)

                if decoded_data_bits is not None:
                    bit_buffer += decoded_data_bits
                    decoded_block_count += 1

                    # Збираємо біти в байти (по 8 біт) і записуємо
                    while len(bit_buffer) >= 8:
                        byte_str = bit_buffer[:8]
                        bit_buffer = bit_buffer[8:]
                        # Перетворюємо рядок '01...' у число
                        byte_val = int(byte_str, 2)
                        # Записуємо байт у вихідний файл
                        outfile.write(bytes([byte_val]))
                else:
                    print("Помилка декодування блоку, пропуск.")


            # Обробка залишку бітів у буфері
            # Якщо ми не зберігали інформацію про реальну довжину останнього блоку,
            # то залишок може містити "сміття" від доповнення нулями при кодуванні.
            # Якщо залишок < 8 біт, ми не можемо сформувати повний байт.
            if bit_buffer:
                 print(f"Попередження: Залишилось {len(bit_buffer)} біт у буфері після декодування.")
                 print("Ці біти можуть бути частиною доповнення останнього блоку і будуть проігноровані,")
                 print("оскільки неможливо сформувати повний байт.")
                 # Для ідеального відновлення потрібен механізм обробки останнього блоку.

        print(f"Файл '{input_filepath}' успішно декодовано у '{output_filepath}'.")
        print(f"Всього оброблено блоків: {decoded_block_count}")

    except FileNotFoundError:
        print(f"Помилка: Вхідний файл '{input_filepath}' не знайдено.")
    except ValueError as e:
         print(f"Помилка перетворення даних: {e}. Можливо, файл пошкоджено або не є закодованим файлом Хемінга.")
    except Exception as e:
        print(f"Сталася помилка під час декодування: {e}")


# --- Головна частина програми (інтерфейс користувача) ---
if __name__ == "__main__":
    while True:
        print("\n--- Кодер/Декодер Хемінга ---")
        mode = input("Оберіть режим: 'encode' (кодувати), 'decode' (декодувати), або 'exit' для виходу: ").strip().lower()

        if mode == 'exit':
            break

        if mode not in ['encode', 'decode']:
            print("Невірний режим. Спробуйте ще раз.")
            continue

        input_filepath = input("Введіть шлях до вхідного файлу: ").strip()
        # Перевіряємо чи існує вхідний файл
        if not os.path.exists(input_filepath):
             print(f"Помилка: Вхідний файл '{input_filepath}' не знайдено. Спробуйте ще раз.")
             continue

        output_filepath = input("Введіть шлях до вихідного файлу: ").strip()

        # Запитуємо довжину інформаційного блоку m
        while True:
            try:
                m_str = input("Введіть довжину інформаційного блоку (m, ціле число > 0, наприклад, 8, 16, 32): ").strip()
                m = int(m_str)
                if m <= 0:
                    print("Довжина блоку має бути позитивним числом.")
                    continue
                # Можна додати перевірку на максимальне значення m, якщо потрібно
                # if m > 4096:
                #      print("Довжина блоку занадто велика для цього прикладу.")
                #      continue
                break # Виходимо з циклу, якщо m коректне
            except ValueError:
                print("Будь ласка, введіть ціле число для довжини блоку.")

        # Виконуємо обрану дію
        if mode == 'encode':
            encode_file(input_filepath, output_filepath, m)
        elif mode == 'decode':
            decode_file(input_filepath, output_filepath, m)

    print("\nРоботу завершено.")