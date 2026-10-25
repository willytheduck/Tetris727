import pygame, random

pygame.init()

PPC = 13  # pixel per cel
PAD = 8  # padding for exported sprite
SCL = 2
CEL = PPC * SCL
OFF = PAD * SCL

COLS, ROW = 10, 20

# layout
MARG = 20
BORD = 8
PW = 5 * CEL
BW, BH = COLS * CEL, ROW * CEL
BX = MARG + PW + MARG + BORD
BY = MARG + BORD
RX = BX + BW + BORD + MARG
W = RX + PW + MARG
H = BH + 2 * (MARG + BORD)

scren = pygame.display.set_mode((W, H))
pygame.display.set_caption("Little Guy Tetris")
clock = pygame.time.Clock()
ft = pygame.font.SysFont(None, 32)
smol = pygame.font.SysFont(None, 24)


# Colours
WIN_BG = (79, 74, 71)
FIL = (60, 56, 64)
BORD_COL = (46, 42, 49)
GRID_L = (70, 65, 74, 140)
TXT = (251, 251, 251)
NEXT = (216, 213, 219)

# shape
SHAPES = {
    "I": [(0, 1), (1, 1), (2, 1), (3, 1)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T": [(1, 0), (0, 1), (1, 1), (2, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
}
# size
SIZES = {"I": 4, "O": 2}


def spin_cells(cells, size):
    return [(size - 1 - cy, cx) for cx, cy in cells]


def normal(cells):
    mx = min(c[0] for c in cells)
    my = min(c[1] for c in cells)
    return [(cx - mx, cy - my) for cx, cy in cells]


def b_tile(kind):
    # each rotation cut sprite into 1 tile p cel
    img = pygame.image.load(f"Assets/{kind}.png").convert_alpha()
    size = SIZES.get(kind, 3)
    cells = list(SHAPES[kind])
    result = []
    for rot in range(4):
        rimg = pygame.transform.rotate(img, -90 * rot)  # clock
        tiles = {}
        for nx, ny in normal(cells):
            rect = pygame.Rect(nx * PPC, ny * PPC, PPC + 2 * PAD, PPC + 2 * PAD)
            tile = rimg.subsurface(rect).copy()
            tile = pygame.transform.scale(tile, (rect.w * SCL, rect.h * SCL))
            tiles[(nx, ny)] = tile
        result.append(tiles)
        cells = spin_cells(cells, size)
    return result


TILE = {kind: b_tile(kind) for kind in SHAPES}

grid_s = pygame.Surface((BW, BH), pygame.SRCALPHA)
for x in range(1, COLS):
    pygame.draw.line(grid_s, GRID_L, (x * CEL, 0), (x * CEL, BH))
for y in range(1, ROW):
    pygame.draw.line(grid_s, GRID_L, (0, y * CEL), (BW, y * CEL))


# piece
class Piece:
    def __init__(self, kind):
        self.kind = kind
        self.size = SIZES.get(kind, 3)
        self.cells = list(SHAPES[kind])
        self.rot = 0
        self.x = COLS // 2 - self.size // 2
        self.y = 0

    def rotatd(self):
        return spin_cells(self.cells, self.size)

    def tiles(self):
        mx = min(c[0] for c in self.cells)
        my = min(c[1] for c in self.cells)
        t = TILE[self.kind][self.rot]
        return [
            ((self.x + cx, self.y + cy), t[(cx - mx, cy - my)]) for cx, cy in self.cells
        ]


# avoiding the same piece over and over
bag = []


def next_fm_bag():
    global bag
    if not bag:
        bag = list(SHAPES)
        random.shuffle(bag)
    return bag.pop()


# game state
grid = [[None] * COLS for _ in range(ROW)]
piece = None
next_p = next_fm_bag()
hold_p = None
can_hold = True
score = 0
lines = 0
game_o = False


def level():
    return lines // 10  # +1 lvl every 10 line


def fail_ms():
    return max(80, 500 - 45 * level())  # every level become fast but never below 80ms


def valid(cells, px, py):
    for cx, cy in cells:
        x, y = px + cx, py + cy
        if x < 0 or x >= COLS or y >= ROW:
            return False
        if y >= 0 and grid[y][x] is not None:
            return False
    return True


def spawn():
    global piece, next_p, can_hold
    piece = Piece(next_p)
    next_p = next_fm_bag()
    can_hold = True
    return valid(piece.cells, piece.x, piece.y)


def dohold_p():
    global piece, hold_p, can_hold, game_o
    if not can_hold:
        return
    if hold_p is None:
        hold_p = piece.kind
        if not spawn():
            game_o = True
    else:
        hold_p, sawp = piece.kind, hold_p
        piece = Piece(sawp)
        if not valid(piece.cells, piece.x, piece.y):
            game_o = True
    can_hold = False


def lock_p():
    global score, lines, game_o
    for (gx, gy), tile in piece.tiles():
        grid[gy][gx] = tile
    remain = [row for row in grid if any(c is None for c in row)]
    clear = ROW - len(remain)
    grid[:] = [[None] * COLS for _ in range(clear)] + remain
    score += [0, 100, 300, 500, 800][clear]
    lines += clear

    if not spawn():
        game_o = True


def reset():
    global grid, bag, next_p, hold_p, score, lines, game_o
    grid = [[None] * COLS for _ in range(ROW)]
    bag = []
    next_p = next_fm_bag()
    hold_p = None
    score = 0
    lines = 0
    game_o = False
    spawn()


spawn()


# draw
def draw_p(x, y, h, label):
    scren.blit(smol.render(label, True, TXT), (x, y - 22))
    r = pygame.Rect(x, y, PW, h)
    pygame.draw.rect(scren, FIL, r, border_radius=6)
    pygame.draw.rect(scren, BORD_COL, r, 4, border_radius=6)
    return r


def draw_pre(kind, r):
    cells = normal(SHAPES[kind])
    w = (max(c[0] for c in cells) + 1) * CEL
    h = (max(c[1] for c in cells) + 1) * CEL
    ox = r.centerx - w // 2
    oy = r.centery - h // 2
    tiles = TILE[kind][0]
    scren.set_clip(r.inflate(-4, -4))
    for cx, cy in cells:
        scren.blit(tiles[(cx, cy)], (ox + cx * CEL - OFF, oy + cy * CEL - OFF))
    scren.set_clip(None)


def draw_a():
    scren.fill(WIN_BG)

    # board
    board_r = pygame.Rect(BX, BY, BW, BH)
    pygame.draw.rect(scren, FIL, board_r)
    scren.blit(grid_s, (BX, BY))
    scren.set_clip(board_r)
    for r, row in enumerate(grid):
        for c, tile in enumerate(row):
            if tile is not None:
                scren.blit(tile, (BX + c * CEL - OFF, BY + r * CEL - OFF))
    for (gx, gy), tile in piece.tiles():
        scren.blit(tile, (BX + gx * CEL - OFF, BY + gy * CEL - OFF))
    scren.set_clip(None)
    pygame.draw.rect(
        scren, BORD_COL, board_r.inflate(2 * BORD, 2 * BORD), BORD, border_radius=6
    )
    box_y = BY + 28
    box_h = 3 * CEL
    # hold piece
    r = draw_p(MARG, box_y, box_h, "HOLD")
    if hold_p:
        draw_pre(hold_p, r)
    next1 = ["Up: rotate", "Space: drop", "C/SHIFT: hold"]
    for i, t in enumerate(next1):
        scren.blit(smol.render(t, True, NEXT), (MARG, box_y + box_h + 24 + i * 24))

    # next + stat
    r = draw_p(RX, box_y, box_h, "NEXT")
    draw_pre(next_p, r)
    sy = box_y + box_h + 24
    for i, t in enumerate(
        [f"Score: {score}", f"Lines: {lines}", f"Level: {level()+1}"]
    ):
        scren.blit(ft.render(t, True, TXT), (RX, sy + i * 34))

    if game_o:
        shade = pygame.Surface((BW, BH), pygame.SRCALPHA)
        shade.fill((46, 42, 49, 200))
        scren.blit(shade, (BX, BY))
        t1 = ft.render("Game over!", True, TXT)
        t2 = smol.render("R to play again", True, TXT)
        scren.blit(t1, (BX + BW // 2 - t1.get_width() // 2, BY + BH // 2 - 24))
        scren.blit(t2, (BX + BW // 2 - t2.get_width() // 2, BY + BH // 2 + 10))
        pygame.draw.rect(
            scren, BORD_COL, board_r.inflate(2 * BORD, 2 * BORD), BORD, border_radius=6
        )


# loop
fal_timer = 0
running = True
while running:
    fal_timer += clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_o:
                if event.key == pygame.K_r:
                    reset()
                    fal_timer = 0
                continue
            if event.key == pygame.K_LEFT and valid(piece.cells, piece.x - 1, piece.y):
                piece.x -= 1
            elif event.key == pygame.K_RIGHT and valid(
                piece.cells, piece.x + 1, piece.y
            ):
                piece.x += 1
            elif event.key == pygame.K_DOWN:
                if valid(piece.cells, piece.x, piece.y + 1):
                    piece.y += 1
                else:
                    lock_p()
            elif event.key == pygame.K_SPACE:  # hard drop
                while valid(piece.cells, piece.x, piece.y + 1):
                    piece.y += 1
                lock_p()
            elif event.key in (pygame.K_c, pygame.K_LSHIFT, pygame.K_RSHIFT):
                dohold_p()
            elif event.key == pygame.K_UP:
                new = piece.rotatd()
                for kick in (0, -1, 1, -2, 2):
                    if valid(new, piece.x + kick, piece.y):
                        piece.cells = new
                        piece.rot = (piece.rot + 1) % 4
                        piece.x += kick
                        break
    if not game_o and fal_timer >= fail_ms():
        fal_timer = 0
        if valid(piece.cells, piece.x, piece.y + 1):
            piece.y += 1
        else:
            lock_p()

    draw_a()
    pygame.display.flip()

pygame.quit()
