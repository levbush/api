import os
import sys
import requests
import arcade

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "MAP"
MAP_FILE = "map.png"


class GameView(arcade.Window):
    def setup(self):
        self.get_image()

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                (self.width - self.background.width) // 2,
                (self.height - self.background.height) // 2,
                self.background.width,
                self.background.height
            ),
        )

    def get_image(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = '0680ad62-62c5-40bb-93fe-f72f890c42df'
        lon = input("Введите lon: ")
        lat = input("Введите lon: ")
        ll_spn = f'll={lon},{lat}&spn=60,40'
        # Готовим запрос.

        map_request = f"{server_address}{ll_spn}&apikey={api_key}"
        print(map_request)
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        with open(MAP_FILE, "wb") as file:
            file.write(response.content)

        self.background = arcade.load_texture(MAP_FILE)


def main():
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    # Удаляем за собой файл с изображением.
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()
