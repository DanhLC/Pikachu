import pyautogui
import cv2
import numpy as np
import time
import keyboard
import os

os.makedirs('log', exist_ok=True)
os.makedirs('tiles', exist_ok=True)
os.makedirs('log_similar', exist_ok=True)

REGION = (1399, 304, (2405-1399), (1005-304))
ROWS, COLS = 9, 16
TILE_SIZE = REGION[2] // COLS

def screenshot_board():
    img = pyautogui.screenshot(region=(1399, 304, (2405-1399), (1005-304)))
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def split_tiles(img):
    tiles = []
    for r in range(9):
        row = []
        for c in range(16):
            tile_img = img[r*TILE_SIZE:(r+1)*TILE_SIZE, c*TILE_SIZE:(c+1)*TILE_SIZE]
            row.append(tile_img)
        tiles.append(row)
    return tiles

def is_blank(tile, threshold=240):
    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
    return np.mean(gray) > threshold

def is_similar(img1, img2, threshold=0.4):
    res = cv2.matchTemplate(img1, img2, cv2.TM_CCOEFF_NORMED)
    val = cv2.minMaxLoc(res)[1]
    if val > threshold:
        cv2.imwrite(f"log_similar/log_similar_{val:.2f}.png", np.hstack((img1, img2)))
    return val > threshold


def build_matrix(tiles):
    matrix, tile_dict, tile_id = [[0]*16 for _ in range(9)], {}, 1
    for r in range(9):
        for c in range(16):
            tile = tiles[r][c]
            if is_blank(tile):
                continue
            matched = False
            for (rr, cc), tid in tile_dict.items():
                if is_similar(tile, tiles[rr][cc]):
                    matrix[r][c] = tid
                    matched = True
                    break
            if not matched:
                tile_dict[(r, c)] = tile_id
                matrix[r][c] = tile_id
                tile_id += 1
            
            cv2.imwrite(f"tiles/tile_{r}_{c}_id_{matrix[r][c]}.png", tile)

    return matrix

def can_connect_straight(matrix, r1, c1, r2, c2):
    if r1 == r2:
        return all(matrix[r1][c]==0 for c in range(min(c1,c2)+1,max(c1,c2)))
    if c1 == c2:
        return all(matrix[r][c1]==0 for r in range(min(r1,r2)+1,max(r1,r2)))
    return False

def can_connect_L(matrix, r1, c1, r2, c2):
    if matrix[r1][c2]==0 and can_connect_straight(matrix,r1,c1,r1,c2) and can_connect_straight(matrix,r1,c2,r2,c2):
        return True
    if matrix[r2][c1]==0 and can_connect_straight(matrix,r1,c1,r2,c1) and can_connect_straight(matrix,r2,c1,r2,c2):
        return True
    return False

def can_connect_U(matrix, r1, c1, r2, c2):
    for r in range(9):
        if matrix[r][c1]==0 and matrix[r][c2]==0 and \
            can_connect_straight(matrix,r1,c1,r,c1) and \
            can_connect_straight(matrix,r,c1,r,c2) and \
            can_connect_straight(matrix,r,c2,r2,c2):
            return True
    for c in range(16):
        if matrix[r1][c]==0 and matrix[r2][c]==0 and \
            can_connect_straight(matrix,r1,c1,r1,c) and \
            can_connect_straight(matrix,r1,c,r2,c) and \
            can_connect_straight(matrix,r2,c,r2,c2):
            return True
    return False

def can_connect(matrix, r1, c1, r2, c2):
    if matrix[r1][c1]!=matrix[r2][c2] or matrix[r1][c1]==0:
        return False
    return can_connect_straight(matrix,r1,c1,r2,c2) or \
           can_connect_L(matrix,r1,c1,r2,c2) or \
           can_connect_U(matrix,r1,c1,r2,c2)

def find_next_pair(matrix):
    directions = [
        [(r, c) for r in range(ROWS) for c in range(COLS)],
        [(r, c) for r in range(ROWS) for c in reversed(range(COLS))],
        [(r, c) for r in reversed(range(ROWS)) for c in range(COLS)],
        [(r, c) for r in reversed(range(ROWS)) for c in reversed(range(COLS))]
    ]
    for order in directions:
        for r1, c1 in order:
            if matrix[r1][c1] == 0:
                continue
            for r2, c2 in order:
                if (r1, c1) != (r2, c2) and matrix[r2][c2] == matrix[r1][c1]:
                    if can_connect(matrix, r1, c1, r2, c2):
                        return r1, c1, r2, c2
    return None

def click(r,c):
    x = REGION[0] + c*TILE_SIZE + TILE_SIZE//2
    y = REGION[1] + r*TILE_SIZE + TILE_SIZE//2
    pyautogui.click(x,y)

def log_match(r1,c1,r2,c2):
    with open("log/log.txt","a",encoding="utf-8") as f:
        f.write(f"({r1},{c1}) ↔ ({r2},{c2})\n")
        
def log_matrix(matrix, file_name="log_matrix.txt"):
    with open(file_name, "w") as f:
        for row in matrix:
            f.write(str(row) + "\n")

print("Bot bắt đầu sau 2 giây...")
time.sleep(2)

while True:
    if keyboard.is_pressed('q'):
          print("🛑 Đã dừng bot")
          break
    time.sleep(0.1)

    img = screenshot_board()
    tiles = split_tiles(img)
    matrix = build_matrix(tiles)

    match = find_next_pair(matrix)
    if match:
        r1,c1,r2,c2=match
        click(r1,c1)
        time.sleep(0.15)
        click(r2,c2)
        log_match(r1,c1,r2,c2)
        time.sleep(0.2)
    else:
        print("🚫 Không còn cặp nối")
        break
