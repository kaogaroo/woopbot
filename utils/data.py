import random

class Board:
    def __init__(self):
        self.cols = [0 for _ in range(10)]
    
    def add_garbage(self, lines: int):
        hole = random.randint(0, 9)
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

if __name__ == "__main__":
    board = Board()
    board.add_garbage(10)
    for col in board.cols:
        print(f"{col:064b}")