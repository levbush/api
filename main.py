import os
import sys
import requests
import arcade
from config import STATIC_API_KEY, GEOCODER_API_KEY


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "MAP"
MAP_FILE = "map.png"


class GameView(arcade.Window):
    def setup(self):
        self.lon = input("Введите lon: ")
        self.lat = input("Введите lat: ")
        self.spn = [60, 40]
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
        api_key = STATIC_API_KEY
        ll_spn = f'll={self.lon},{self.lat}&spn={self.spn[0]},{self.spn[1]}'
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

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP:
            self.spn[0] += 1
            self.spn[1] += 1
        if key == arcade.key.DOWN:
            self.spn[0] -= 1
            self.spn[1] -= 1

        if self.spn[0] <= 1:
            self.spn = 1
        elif self.spn[0] >= 70:
            self.spn = 70
        
        if self.spn[1] <= 1:
            self.spn = 1
        elif self.spn[1] >= 70:
            self.spn = 70
            
        os.remove(MAP_FILE)
        self.get_image()

def main():
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    # Удаляем за собой файл с изображением.
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()
