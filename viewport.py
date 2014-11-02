from sys import exit as sys_exit
from random import randint
import pygame as pg


class WorldMap(object):
    def __init__(self, size=(3200, 3200)):
        tree_img = pg.image.load("tree.png").convert()
        tree_img.set_colorkey(pg.Color("black"))
        building_img = pg.image.load("pottingshed.png")
        building_img.set_colorkey(pg.Color("black"))
        self.surf = pg.Surface(size).convert()
        self.surf.fill(pg.Color("darkgreen"))
        w, h = size
        for _ in range(10):
            pos = (randint(50, w - 50), randint(50, h - 50))
            self.surf.blit(building_img, pos)
        for _ in range(200):
            pos = (randint(50, w - 50), randint(50, h - 50))
            self.surf.blit(tree_img, pos)


class Viewport(object):
    """A simple viewport/camera to handle scrolling and zooming a surface."""

    def __init__(self, base_map, view_size=(800, 800)):
        """The base_map argument should be a pygame.Surface object.
            Works best with view_size[0] == view_size[1]"""
        self.base_map = base_map
        self.base_rect = self.base_map.get_rect()
        self.zoom_levels = {}
        for i in range(10):
            self.zoom_levels[i] = (self.base_rect.width // 2**i,
                                             self.base_rect.height // 2**i)
        self.zoom_level = 0
        self.max_zoom = len(self.zoom_levels) - 1
        self.view_size = view_size
        self.zoom_rect = pg.Rect((0, 0), self.zoom_levels[self.zoom_level])
        self.scroll_margin = 20
        self.scroll_speed = 5
        self.scroll([0, 0])

    def scroll(self, offset):
        """Move self.room_rect by offset and update image."""
        self.zoom_rect.move_ip(offset)
        self.zoom_rect.clamp_ip(self.base_rect)
        self.zoom_image()

    def zoom_image(self):
        """Set self.zoomed_image to the properly scaled subsurface."""
        subsurface = self.base_map.subsurface(self.zoom_rect)
        self.zoomed_image = pg.transform.scale(subsurface, self.view_size)

    def get_map_pos(self, screen_pos):
        """Takes in a tuple of screen coordinates and returns a tuple of
            the screen_position translated to the proper map coordinates
            for the current zoom level."""
        view_width, view_height = self.view_size
        x, y = screen_pos
        x_scale = self.zoom_levels[self.zoom_level][0] / float(view_width)
        y_scale = self.zoom_levels[self.zoom_level][1] / float(view_height)
        mapx = self.zoom_rect.left + (x * x_scale)
        mapy = self.zoom_rect.top + (y * y_scale)
        return mapx, mapy

    def get_zoom_rect(self, mapx, mapy):
        """Return a Rect of the current zoom resolution centered at mapx, mapy."""
        zoom_rect = pg.Rect((0, 0), self.zoom_levels[self.zoom_level])
        zoom_rect.center = (mapx, mapy)
        zoom_rect.clamp_ip(self.base_rect)
        return zoom_rect

    def get_event(self, event):
        """Respond to MOUSEBUTTONDOWN events, zooming in on
            left click and out on right click."""
        if event.button == 1:
            if self.zoom_level < self.max_zoom:
                mapx, mapy = self.get_map_pos(event.pos)
                self.zoom_level += 1
                self.zoom_rect = self.get_zoom_rect(mapx, mapy)
                self.zoom_image()

        elif event.button == 3:
            if self.zoom_level > 0:
                mapx, mapy = self.get_map_pos(event.pos)
                self.zoom_level -= 1
                self.zoom_rect = self.get_zoom_rect(mapx, mapy)
                self.zoom_image()

    def update(self):
        """Check for scrolling each frame."""
        mouse_pos = pg.mouse.get_pos()
        offset = [0, 0]
        if mouse_pos[0] < self.scroll_margin:
            offset[0] -= self.scroll_speed
        elif mouse_pos[0] > self.view_size[0] - self.scroll_margin:
            offset[0] += self.scroll_speed
        if mouse_pos[1] < self.scroll_margin:
            offset[1] -= self.scroll_speed
        elif mouse_pos[1] > self.view_size[1] - self.scroll_margin:
            offset[1] += self.scroll_speed
        if offset != [(0, 0)]:
            self.scroll(offset)

    def draw(self, surface):
        surface.blit(self.zoomed_image, (0, 0))


class Game(object):
    """Just a quick game skeleton to test out the viewport."""
    def __init__(self):
        self.screen = pg.display.set_mode((800, 800))
        self.clock = pg.time.Clock()
        self.fps = 60
        self.done = False
        self.world_map = WorldMap()
        self.viewport = Viewport(self.world_map.surf)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.viewport.get_event(event)

    def update(self):
        self.viewport.update()

    def draw(self):
        self.viewport.draw(self.screen)

    def run(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.update()
            self.clock.tick(self.fps)
            pg.display.set_caption("FPS: {}".format(self.clock.get_fps()))

if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
    pg.quit()
    sys_exit()