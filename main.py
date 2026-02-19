import os
import sys
import requests
import arcade
from config import STATIC_API_KEY, GEOCODER_API_KEY
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UIFlatButton

SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
WINDOW_TITLE = "MAP"
ADD_ZOOM = 0.1
STEP = 0.2
MAP_FILE = "map.png"


class GameView(arcade.Window):
    def __init__(self, *args):
        super().__init__(*args)
        self.manager = UIManager()
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout()
        self.button = UIFlatButton()
        self.button.text = 'Change theme'
        self.button.on_click = lambda _: self.change_theme()
        self.box_layout.add(self.button)
        self.anchor_layout.add(self.box_layout, anchor_y='bottom', align_y=50)
        self.manager.add(self.anchor_layout)
        self.manager.enable()

        self.theme_white = True

    def setup(self):
        self.lon = float(input("Введите lon: "))
        self.lat = float(input("Введите lat: "))
        self.spn = [20, 20]
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
        self.manager.draw()

    def get_image(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = STATIC_API_KEY
        ll_spn = f'll={self.lon},{self.lat}&spn={self.spn[0]},{self.spn[1]}'
        # Готовим запрос.

        map_request = f"{server_address}{ll_spn}&apikey={api_key}&theme={'light' if self.theme_white else 'dark'}"
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
        if arcade.key.LEFT == key or arcade.key.A == key:
            self.lon -= STEP
        if arcade.key.RIGHT == key or arcade.key.D == key:
            self.lon += STEP
        if arcade.key.UP == key or arcade.key.W == key:
            self.lat += STEP
        if arcade.key.DOWN == key or arcade.key.S == key:
            self.lat -= STEP
        
        if key == arcade.key.PAGEDOWN:
            self.spn[0] += ADD_ZOOM
            self.spn[1] += ADD_ZOOM
        if key == arcade.key.PAGEUP:
            self.spn[0] -= ADD_ZOOM
            self.spn[1] -= ADD_ZOOM

        if self.spn[0] <= 1:
            self.spn = 1
        elif self.spn[0] >= 40:
            self.spn = 40
        
        if self.spn[1] <= 1:
            self.spn = 1
        elif self.spn[1] >= 40:
            self.spn = 40
            
        os.remove(MAP_FILE)
        self.get_image()

    def change_theme(self):
        self.theme_white = not self.theme_white
        self.get_image()

def main():
    gameview = GameView(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    # Удаляем за собой файл с изображением.
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()
