import os
import sys
import requests
import arcade
from config import STATIC_API_KEY, GEOCODER_API_KEY
from arcade.gui import UIManager, UIAnchorLayout, UIBoxLayout, UIFlatButton, UIInputText

SCREEN_WIDTH, SCREEN_HEIGHT = arcade.window_commands.get_display_size()
WINDOW_TITLE = "MAP"
ZOOM_FACTOR = 0.75
MAP_FILE = "map.png"


class GameView(arcade.Window):
    def __init__(self, *args):
        super().__init__(*args)
        arcade.set_background_color(arcade.color.WHITE)
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

        self.search_query_area = UIInputText(text_color=arcade.color.BLACK, border_color=arcade.color.DARK_BLUE_GRAY, caret_color=arcade.color.BLACK)
        self.search_query_area.width = 400
        
        self.box_layout.add(self.theme_button)
        self.box_layout.add(self.maptype_button)
        self.box_layout.add(self.search_query_area)
        self.anchor_layout.add(self.box_layout, anchor_y='top', align_y=-50, anchor_x='left', align_x=15)
        self.manager.add(self.anchor_layout)
        self.manager.enable()

        self.theme_white = True
        self.maptypes = ['map', 'driving', 'transit', 'admin']
        self.curr_maptype = 0

    def setup(self):
        self.keys_pressed = set()
        self.lon = 10
        self.lat = 10
        self.spn = [20, 20]
        self.get_image()

    def on_draw(self):
        self.clear()

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(SCREEN_WIDTH / 2 - SCREEN_HEIGHT / 2, 0, SCREEN_HEIGHT, SCREEN_HEIGHT))
        self.manager.draw()

    def get_image(self):
        server_address = 'https://static-maps.yandex.ru/v1'
        api_key = STATIC_API_KEY

        params = {
            'll': f'{self.lon},{self.lat}',
            'spn': f'{self.spn[0]},{self.spn[1]}',
            'apikey': api_key,
            'theme': 'light' if self.theme_white else 'dark',
            'maptype': self.maptypes[self.curr_maptype],
            'size': '450,450',
            'lang': 'ru_RU'
        }

        response = requests.get(server_address, params=params)


        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        with open(MAP_FILE, "wb") as file:
            file.write(response.content)

        self.background = arcade.load_texture(MAP_FILE)

        os.remove(MAP_FILE)

    def on_key_press(self, key, modifiers):
        self.keys_pressed.add(key)
        
        if arcade.key.LEFT in self.keys_pressed:
            self.lon -= self.spn[0]
        if arcade.key.RIGHT in self.keys_pressed:
            self.lon += self.spn[0]
        if arcade.key.UP in self.keys_pressed:
            self.lat += self.spn[1]
        if arcade.key.DOWN in self.keys_pressed:
            self.lat -= self.spn[1]
        
        if arcade.key.PAGEDOWN in self.keys_pressed:
            self.spn[0] /= ZOOM_FACTOR
            self.spn[1] /= ZOOM_FACTOR
        if arcade.key.PAGEUP in self.keys_pressed:
            self.spn[0] *= ZOOM_FACTOR
            self.spn[1] *= ZOOM_FACTOR

        if self.spn[0] <= .001:
            self.spn[0] = .001
        elif self.spn[0] >= 40:
            self.spn[0] = 40
        
        if self.spn[1] <= .001:
            self.spn[1] = .001
        elif self.spn[1] >= 40:
            self.spn[1] = 40

        if key == arcade.key.ENTER and self.search_query_area.text:
            self.lon, self.lat, self.spn = self.get_ll_spn(self.search_query_area.text)
            
        self.get_image()

    def get_ll_spn(self, geocode):
        server_address = 'https://geocode-maps.yandex.ru/v1?'
        api_key = GEOCODER_API_KEY

        response = requests.get(server_address, params={'geocode': geocode, 'apikey': api_key, 'format': 'json', 'results': 1})

        if response.status_code != 200:
            return self.lon, self.lat
        data = response.json()
        if not data['response']['GeoObjectCollection']['metaDataProperty']['GeocoderResponseMetaData']['found']:
            return self.lon, self.lat
        toponym = data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
        return *map(float, toponym['Point']['pos'].split()), self.toponym_to_spn(toponym)

    def on_key_release(self, key, modifiers):
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

    def change_theme(self):
        self.theme_white = not self.theme_white
        self.get_image()

    def change_maptype(self):
        self.curr_maptype = (self.curr_maptype + 1) % len(self.maptypes)
        self.get_image()

    @staticmethod
    def toponym_to_spn(toponym) -> tuple[float]:
        bounds = tuple(map(float, toponym['boundedBy']['Envelope']['lowerCorner'].split())), tuple(
            map(float, toponym['boundedBy']['Envelope']['upperCorner'].split())
        )
        return (abs(bounds[0][0] - bounds[1][0]), abs(bounds[0][1] - bounds[1][1]))


def main():
    gameview = GameView(SCREEN_WIDTH, SCREEN_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    # Удаляем за собой файл с изображением.


if __name__ == "__main__":
    main()
