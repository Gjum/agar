from time import time
from agario.vec import Vec

from .subscriber import Subscriber
from .drawutils import *


class RemergeTimes(Subscriber):
    def __init__(self, client):
        self.client = client

    def on_own_id(self, cid):
        self.client.player.world.cells[cid].split_time = time()

    def on_draw_cells(self, c, w):
        p = self.client.player
        if len(p.own_ids) <= 1:
            return  # dead or only one cell, no remerge time to display
        now = time()
        for cell in p.own_cells:
            split_for = now - cell.split_time
            # formula by DebugMonkey
            ttr = (p.total_mass * 20 + 30000) / 1000 - split_for
            if ttr < 0: continue
            pos = w.world_to_screen_pos(cell.pos)
            text = 'TTR %.1fs after %.1fs' % (ttr, split_for)
            draw_text_center(c, Vec(0, -12).iadd(pos), text)


class CellMasses(Subscriber):
    def on_draw_cells(self, c, w):
        p = self.client.player
        for cell in p.world.cells.values():
            if cell.is_food or cell.is_ejected_mass:
                continue
            pos = w.world_to_screen_pos(cell.pos)
            if cell.name:
                pos.iadd(Vec(0, 12))
            text = '%i mass' % cell.mass
            draw_text_center(c, pos, text)


class CellHostility(Subscriber):
    def on_draw_cells(self, c, w):
        p = self.client.player
        if not p.is_alive: return  # nothing to be hostile against
        own_min_mass = min(c.mass for c in p.own_cells)
        own_max_mass = max(c.mass for c in p.own_cells)
        lw = c.get_line_width()
        c.set_line_width(5)
        for cell in p.world.cells.values():
            if cell.is_food or cell.is_ejected_mass:
                continue  # no threat
            if cell.cid in p.own_ids:
                continue  # own cell, also no threat lol
            pos = w.world_to_screen_pos(cell.pos)
            color = YELLOW
            if cell.is_virus:
                if own_max_mass > cell.mass:
                    color = RED
                else:
                    continue  # no threat, do not mark
            elif own_min_mass > cell.mass * 1.25 * 2:
                color = PURPLE
            elif own_min_mass > cell.mass * 1.25:
                color = GREEN
            elif cell.mass > own_min_mass * 1.25 * 2:
                color = RED
            elif cell.mass > own_min_mass * 1.25:
                color = ORANGE
            c.set_source_rgba(*color)
            draw_circle_outline(c, pos, cell.size * w.screen_scale)
        c.set_line_width(lw)
