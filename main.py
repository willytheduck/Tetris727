import pygame, random

pygame.init()

PPC = 13 # pixel per cel
PAD = 8 # padding for exported sprite
SCL = 2 
CEL = PPC * SCL
OFF = PAD * SCL

COLS, ROW = 10,20
W,H = COLS*CEL+200, ROW*CEL
scren = pygame.display.set_mode((W,H))
pygame.display.set_caption("Little Guy Tetris")
clock = pygame.time.Clock()
ft = pygame.font.SysFont(None, 32)

BG = (46, 42, 49)
GRID = (79,74,71)
TEXT = (251, 251, 251)

#shape
SHAPES = {
    'I': [(0, 1), (1, 1), (2, 1), (3, 1)],
    'O': [(0, 0), (1, 0), (0, 1), (1, 1)],
    'T': [(1, 0), (0, 1), (1, 1), (2, 1)],
    'S': [(1, 0), (2, 0), (0, 1), (1, 1)],
    'Z': [(0, 0), (1, 0), (1, 1), (2, 1)],
    'J': [(0, 0), (0, 1), (1, 1), (2, 1)],
    'L': [(2, 0), (0, 1), (1, 1), (2, 1)],
}
#size
SIZES = {'I': 4, 'O': 2}

def spin_cels(cells, size):
    return [(size-1-cy,cx) for cx,cy in cells]

def normal(cells):
    mx = min(c[0] for c in cells)
    my = min(c[1] for c in cells)
    return [(cx - mx, cy - my) for cx,cy in cells]

def b_tile(kind):
    #each rotation cut sprite into 1 tile p cel
    img = pygame.image.load(f"Assets/{kind}.png").convert_alpha()
    size = SIZES.get(kind,3)
    cells = list(SHAPES[kind])
    result = []
    for rot in range(4):
        rimg = pygame.transform.rotate(img, -90 * rot) #clock
        tiles = {}
        for nx, ny in normal(cells):
            rect = pygame.Rect(nx * PPC, ny * PPC, PPC +2*PAD, PPC+2*PAD)
            tile = rimg.subsurface(rect).copy
            tile = pygame.transform.scale(tile,(rect.w *SCL, rect.h * SCL))
            tiles[(nx,ny)] = tile
        result.append(tiles)
        cells = spin_cels(cells,size)
    return result
TILE = {kind: b_tile(kind) for kind in SHAPES}

#piece
class Piece:
    def __init__(self,kind):
        self.kind = kind
        self.size = SIZES.get(kind,3)
        self.cells = list(SHAPES[kind])
        self.rot = 0
        self.x = COLS//2 -self.size//2
        self.y = 0

    def rotatd(self):
        return spin_cels(self.cells,self.size)


    def tiles(self):
        mx = min(c[0] for c in self.cells)
        my = min(c[1] for c in self.cells)
        t = TILE[self.kind][self.rot]
        return [((self.x+cx, self.y+cy), t[(cx-mx, cy-my)])for cx,cy in self.cells]
