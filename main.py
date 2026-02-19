import os
import sys
import requests
import arcade
from config import STATIC_API_KEY, GEOCODER_API_KEY
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UIFlatButton

SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
WINDOW_TITLE = "MAP"
ADD_ZOOM = 0.005
STEP = SCREEN_WIDTH
MAP_FILE = "map.png"


class GameView(arcade.Window):
    def __init__(self, *args):
        super().__init__(*args)
        self.manager = UIManager()
        self.anchor_layout = UIAnchorLayout()
        self.box_layout = UIBoxLayout()
        
        self.theme_button = UIFlatButton()
        self.theme_button.text = 'Change theme'
        self.theme_button.on_click = lambda _: self.change_theme()
        self.theme_button.width = 250
        
        self.maptype_button = UIFlatButton()
        self.maptype_button.text = 'Change map type'
        self.maptype_button.on_click = lambda _: self.change_maptype()
        self.maptype_button.width = 300
        
        self.box_layout.add(self.theme_button)
        self.box_layout.add(self.maptype_button)
        self.anchor_layout.add(self.box_layout, anchor_y='bottom', align_y=50)
        self.manager.add(self.anchor_layout)
        self.manager.enable()

        self.theme_white = True
        self.maptypes = ['map', 'driving', 'transit', 'admin']
        self.curr_maptype = 0

    def setup(self):
        self.keys_pressed = set()
        self.lon = float(input("Введите lon: "))
        self.lat = float(input("Введите lat: "))
        self.spn = [20, 20]
        self.get_image()

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(SCREEN_WIDTH / 2 - SCREEN_HEIGHT / 2, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
        self.manager.draw()

    def get_image(self):
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = STATIC_API_KEY
        ll_spn = f'll={self.lon},{self.lat}&spn={self.spn[0]},{self.spn[1]}'
        # Готовим запрос.

        map_request = f"{server_address}{ll_spn}&apikey={api_key}&theme={'light' if self.theme_white else 'dark'}&maptype={self.maptypes[self.curr_maptype]}&size=450,450&lang=ru_RU"
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
        
        if arcade.key.PAGEDOWN in self.keys_pressed:
            self.spn[0] += ADD_ZOOM
            self.spn[1] += ADD_ZOOM
        if arcade.key.PAGEUP in self.keys_pressed:
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

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def change_theme(self):
        self.theme_white = not self.theme_white
        self.get_image()

    def change_maptype(self):
        self.curr_maptype = (self.curr_maptype + 1) % len(self.maptypes)
        self.get_image()

def main():
    gameview = GameView(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    # Удаляем за собой файл с изображением.
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()
