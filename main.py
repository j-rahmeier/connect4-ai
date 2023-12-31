import asyncio
import websockets


#128.113.139.63:5000
def make_move(board):
  player = ['o', 's']
  print(type(board), 'make move')
  #array of 1's
  boRD = list(board)
  two = -1
  three = -1
  four = -1

  for c in range(7):
    print("--")
    
    for r in range(6):
      print(board[r])
      if board[r][c] == 1:
        return c
      else:
        if board[r][c] == 2:
          two = c
        if board[r][c] == 3:
          three = c
        if board[r][c] == 4:
          four = c
  if two != -1 and board[0][two] not in player:
    return two
  if three != -1 and board[0][two] not in player:
    return three
  if four != -1 and board[0][two] not in player:
    return four

  return None

def calculate_move(column, board):
  print(type(board), 'calc move')
  print("AAAAAAAAA")
  board = update_board(column, "o", board)
  col = make_move(board)
  return col
  
'''
Updates the board given the collumn played, the player ('s' or 'o'), 
and the board array. Returns board with recalculated weights.
'''
def update_board(col, player, board):
  col = int(col)
  for i in range(6):
    if board[i][col] != 's' and board[i][col]!='o':
      board[i][col]=player
      break

  board = recalculate_weight(board)
  return board

'''
Calculates possible moves and priorities to be used later when deciding
the next move.
favorable:
1: making this move will result in a win (4 s in a row)
2: making this move will block an opponent win (ex.: 2 | o | o | o)
avoid:
3: should play most bc even
4: random option - neutral
5: prob smart not to play
'''
def recalculate_weight(board):
  board = recalculation(board, 1)
  board = recalculation(board, 2)
  return board

'''
d = dir
check_for - if 1 then s, 2 then o
'''
def recalculation(board, check_for):
  #check rows
  for row in board:
    for col in range(4):
      in_row = 0
      blank = (0, 0) #check default
      if row[col]=="s" or row[col] == "o":
        for i in range(1, 4):
          if row[col] == row[col + i]:
            in_row += 1
          else:
            blank = (row, col+1)
        f_num = int(float_num(blank, board))
        if in_row == 3 and f_num == 0:
          board[blank[0]][blank[1]] = check_for
        else:
          if f_num % 2 == 1: #if odd, play bc smort move
            board[blank[0]][blank[1]] = 3
          else: #if even, avoid cuz other can play and make it a 4
            board[blank[0]][blank[1]] = 5

      if row[col] == " ":
        blank = (row, col)
        for i in range(1, 4):
          if row[col + 1] == row[col + i] and row[col + 1] != " ":
            in_row += 1
          else:
            blank = (row, col+1)
          if in_row == 3 and float_num(blank, board) == 0:
            board[blank[0]][blank[1]] = check_for
            
  #check cols
  for col_i in range(7):
    #checks for random
    if uninterupted((0, col_i), board):
      board[0][col_i] = 4
    for row_i in range(5, -1, -1): #starts at row 6, goes up to 0
      in_row = 0
      if board[row_i][col_i]!="s" or board[row_i][col_i]!="o":
        for i in range(1, 3):
          if board[row_i][col_i]==board[row_i - i][col_i]:
            in_row += 1
        if in_row == 3 and board[row_i+3][col_i]==" ":
            board[0][col_i] = check_for
 
'''
Checks how much it's floating
'''
def float_num(blank, board):
  blank_count = 0
  b_row = int(blank[0])
  b_col = int(blank[1])

  for col in range(b_col+1, 6):
    if board[b_row][col] != 's' and board[b_row][col] != 'o':
      blank_count += 1
    
  return blank_count
    

'''
checks if possible to either reach bottom or only a piece
'''
def uninterupted(blank, board):
  b_row = blank[0]
  b_col = blank[1]

  for col in range(b_col+1, 6):
    if board[b_row][col] != ' ' and board[b_row][col] != 's' and  board[b_row][col] != 'o':
      return False
  return True
      


async def gameloop (socket, created, board):
  active = True
  while active:
    
    message = (await socket.recv()).split(':')
    print(message)

    match message[0]:
      case 'GAMESTART':
        move = 3
        await socket.send(f'PLAY:{move}')
      case'OPPONENT':
        print(message[1])
        print("AAAAAA")
        move = calculate_move(message[1], board)
        print(move)
        await socket.send(f'PLAY:{move}')
        
      case 'WIN' | 'LOSS' | 'DRAW' | 'TERMINATED':
        print(message[0])

        active = False

async def create_game (server):
  board = list([[" " for _ in range(7)] for _ in range(6)])
  async with websockets.connect(f'ws://{server}/create') as socket:
    await gameloop(socket, True, board)

async def join_game(server, id):
  board = list([[" " for _ in range(7)] for _ in range(6)])
  async with websockets.connect(f'ws://{server}/join/{id}') as socket:
    await gameloop(socket, False, board)

if __name__ == '__main__':
  board = [[" " for _ in range(7)] for _ in range(6)]

  server = input('Server IP: ').strip()


  protocol = input('Join game or create game? (j/c): ').strip()

  match protocol:
    case 'c':
      asyncio.run(create_game(server))
    case 'j':
      id = input('Game ID: ').strip()

      asyncio.run(join_game(server, id))
    case _:
      print('Invalid protocol!')