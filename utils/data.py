from random import randint
from enum import IntEnum

class Piece(IntEnum):
    I = 0
    O = 1
    T = 2
    S = 3
    Z = 4
    J = 5
    L = 6

class Rotation(IntEnum):
    North = 0
    East = 1
    South = 2
    West = 3
    
    def rotate_block(self, xy):
        x,y = xy
        if self == Rotation.North:
            return (x, y)
        elif self == Rotation.East:
            return (y, -x)
        elif self == Rotation.South:
            return (-x, -y)
        elif self == Rotation.West:
            return (-y, x)
    
    def rotate_blocks(self, minos):
        return [self.rotate_block(m) for m in minos]
    
    def rotate_cw(self):
        return Rotation((self + 1) % 4)
    
    def rotate_ccw(self):
        return Rotation((self - 1) % 4)
    
    def rotate_180(self):
        return Rotation((self + 2) % 4)


UNROTATED = {
    Piece.Z: [(-1, 1), (0, 1), (0, 0), (1, 0)],
    Piece.S: [(-1, 0), (0, 0), (0, 1), (1, 1)],
    Piece.I: [(-1, 0), (0, 0), (1, 0), (2, 0)],
    Piece.O: [(0, 0), (1, 0), (0, 1), (1, 1)],
    Piece.J: [(-1, 0), (0, 0), (1, 0), (-1, 1)],
    Piece.L: [(-1, 0), (0, 0), (1, 0), (1, 1)],
    Piece.T: [(-1, 0), (0, 0), (1, 0), (0, 1)],
}

LUT = [[None for _ in range(4)] for _ in range(7)]
for p in Piece:
    base = UNROTATED[p]
    for r in Rotation:
        LUT[p][r] = tuple(r.rotate_blocks(base)) 

class PieceLocation:
    def __init__(self, piece: Piece, rotation: Rotation, x: int, y: int):
        self.piece = piece
        self.rotation = rotation
        self.x = x
        self.y = y
    
    def translate(self, xy):
        x,y = xy
        return (self.x + x, self.y + y)
    
    def translate_blocks(self, cells):
        return [self.translate(c) for c in cells]

    def blocks(self):
        return self.translate_blocks(LUT[self.piece][self.rotation])
    
    def with_offset(self, dx, dy):
        return PieceLocation(self.piece, self.x + dx, self.y + dy, self.rotation)
    
    def with_rotation(self, rotation):
        return PieceLocation(self.piece, self.x, self.y, rotation)

class Board:
    def __init__(self):
        self.cols = [0 for _ in range(10)]
    
    def add_garbage(self, lines: int):
        hole = randint(0, 9)
        for x in range(10):
            if x == hole:
                self.cols[x] <<= lines
            else:
                self.cols[x] = ~((~self.cols[x]) << lines)

    def put_piece(self, loc):
        for x, u in loc.blocks():
            self.cols[x] |= (1 << u)
        
    def obstructed(self, loc) -> bool:
        for x, u in loc.blocks():
            if (self.cols[x] >> u) & 1:
                return True
        return False
    
    def distance_to_ground(self, loc) -> int:
        dists = []
        for (x, y) in loc.blocks():
            if y == 0:
                dists.append(0)
                continue

            col = self.cols[x]
            mask = (~col) << (64 - y)

            count = 0
            for i in range(63, -1, -1):
                if (mask >> i) & 1 == 1:
                    count += 1
                else:
                    break

            dists.append(count)

        return min(dists)
    
    def remove_lines(self) -> int:
        full = self.cols[0]
        for c in self.cols[1:]:
            full &= c   
        lines = full & ((1 << 64) - 1)
        for i in range(10):
            self.cols[i] = self._clear_lines(self.cols[i], lines)

    def _clear_lines(self, col: int, lines: int) -> int:
        # Clear lines indicated by `lines` and collapse above rows down
        mask64 = (1 << 64) - 1
        col &= mask64
        lines &= mask64
        while lines != 0:
            # isolate lowest set bit
            lowest = lines & -lines
            i = lowest.bit_length() - 1  # index of lowest 1 bit
            mask = (1 << i) - 1  # bits below i
            # keep below i, shift everything above i down by 1
            col = (col & mask) | ((col >> 1) & ~mask & mask64)
            # remove that bit from lines and shift remaining bits down
            lines &= ~(1 << i)
            lines >>= 1
        return col & mask64