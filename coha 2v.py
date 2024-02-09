from PIL import Image
import numpy as np


# def encrypt(image_path, message):
#     # Открыть изображение
#     img = Image.open(image_path)
#     pixels = img.load()
#     width, height = img.size

#     # Конвертировать сообщение в двоичный формат
#     binary_message = ''.join(format(ord(char), '08b') for char in message)

#     # Добавить длину сообщения в начало
#     binary_message = format(len(binary_message), '032b') + binary_message

#     count = 0

#     # Убедиться, что сообщение можно вместить в изображение
#     if len(binary_message) > width * height / 64:
#         raise ValueError("Слишком длинное сообщение для данного изображения")

#     # Шифрование данных
#     message_index = 0
#     for y in range(0, height - 7, 8):
#         for x in range(0, width - 7, 8):
#             bmatrix = [[pixels[x1, y1][2] for x1 in range(x, x+8)] for y1 in range(y, y+8)]
#             # print(bmatrix)
#             dct_matrix = np.zeros_like(bmatrix, dtype=float)
#             for u in range(8):
#                 for v in range(8):
#                     cu = 1 / np.sqrt(2) if u == 0 else 1
#                     cv = 1 / np.sqrt(2) if v == 0 else 1
#                     sum_val = 0
#                     for x in range(8):
#                         for y in range(8):
#                             sum_val += bmatrix[x][y] * np.cos((2 * x + 1) * u * np.pi / 16) * np.cos(
#                                 (2 * y + 1) * v * np.pi / 16)
#                     dct_matrix[u][v] = cu * cv * sum_val / 4

#             # print(dct_matrix)
#             if binary_message[count] == 0:
#                 dct_matrix[4][5] = abs(dct_matrix[5][4]) + 26
#             else:
#                 dct_matrix[5][4] = abs(dct_matrix[4][5]) + 26

#             reconstructed_matrix = np.zeros_like(dct_matrix, dtype=float)

#             for x1 in range(8):
#                 for y1 in range(8):
#                     sum_val = 0
#                     for u in range(8):
#                         for v in range(8):
#                             cu = 1 / np.sqrt(2) if u == 0 else 1
#                             cv = 1 / np.sqrt(2) if v == 0 else 1
#                             sum_val += cu * cv * dct_matrix[u][v] * np.cos((2 * x + 1) * u * np.pi / 16) * np.cos(
#                                 (2 * y + 1) * v * np.pi / 16)
#                     reconstructed_matrix[x][y] = sum_val / 4
#             for x1 in range(8):
#                 for y1 in range(8):
#                     pixels[x + x1, y + y1] = (pixels[x, y][0], pixels[x, y][1], round(reconstructed_matrix[x1, y1]))
#             count += 1
#             if count == len(binary_message):
#                 img.save("modified_image.jpg")
#                 raise MemoryError



def decrypt(image_path):
    # Открыть изображение
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size

    # Инициализировать переменные для хранения длины сообщения и битов сообщения
    message_length_bits = ''
    message_bits = ''

    # Пройти по каждому блоку 8x8 пикселей в изображении
    for y in range(0, height - 7, 8):
        for x in range(0, width - 7, 8):
            dct_matrix = np.zeros((8, 8), dtype=float)

            # Выполнить обратное ДКП для каждого блока пикселей
            for u in range(8):
                for v in range(8):
                    sum_val = 0
                    for x1 in range(8):
                        for y1 in range(8):
                            cu = 1 / np.sqrt(2) if x1 == 0 else 1
                            cv = 1 / np.sqrt(2) if y1 == 0 else 1
                            sum_val += cu * cv * pixels[x + x1, y + y1][2] * np.cos((2 * u + 1) * x1 * np.pi / 16) * np.cos((2 * v + 1) * y1 * np.pi / 16)
                    dct_matrix[u][v] = sum_val / 4

            # Извлечь информацию о бите из измененного коэффициента ДКП в блоке
            bit = 1 if abs(dct_matrix[4][5]) > abs(dct_matrix[5][4]) else 0
            message_bits += str(bit)

            # Собрать биты сообщения и получить его длину из первых 32 битов
            if len(message_length_bits) < 32:
                message_length_bits += str(bit)
            else:
                # Когда получена длина сообщения, извлечь остальные биты
                message_length = int(message_length_bits, 2)
                if len(message_bits) >= message_length:
                    message = ''
                    for i in range(message_length):
                        byte = message_bits[i * 8:(i + 1) * 8]
                        message += chr(int(byte, 2))
                    return message

    return "Сообщение не найдено"

# Пример использования
# image_path = '0-1.jpg'
# message_to_encrypt = "Hello worldik!"

# # Шифрование сообщения в изображение
# encrypt(image_path, message_to_encrypt)


# Пример использования
decrypted_message = decrypt("modified_image.jpg")
print("Decrypted message:", decrypted_message)

# # Расшифровка сообщения из изображения
# decrypted_message = decrypt('encrypted_image.png')
# print("Расшифрованное сообщение:", decrypted_message)