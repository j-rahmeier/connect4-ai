import asyncio
import websockets
import random


#128.113.139.63:5000
def make_move():
  global board
  player = ['o', 's']
  #array of 1's
  boRD = list(board)
  two = -1
  three = -1
  four = -1

  for c in range(7):
    
    for r in range(6):
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

def calculate_move(column):
  global board
  update_board(column, 'o')
  col = make_move()
  return col
  
'''
Updates the board given the collumn played, the player ('s' or 'o'), 
and the board array. Returns board with recalculated weights.
'''
def update_board(col, player):
  global board
  col = int(col)
  for i in range(5, -1, -1):
    if board[i][col] != 's' and board[i][col]!='o':
      board[i][col] = player
      break

  recalculate_weight()

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
def recalculate_weight():
  global board
  recalculation(1)
  #recalculation(2)
  
  
  

'''
d = dir
check_for - if 1 then s, 2 then o
'''
def recalculation(check_for):
  global board

  #check rows
  for row_i in range(6):
    for col in range(4):
      row = board[row_i]
      in_row = 0
      blank = (-1, -1) #check default
      if row[col]=="s" or row[col] == "o":
        for i in range(1, 4):
          if row[col] == row[col + i]:
            in_row += 1
          else:
            if row[col + i] == ' ':
              print("blank r, c: v")
              print((row_i, col + i))
              blank = (row_i, col+i)
        if blank[0] != -1:
          print("blank: v")
          print(blank)
          f_num = int(float_num(blank))
          print("fnum v")
          print(f_num)
          if in_row == 3 and f_num == 0:
            if row[col] == 's':
              board[int(blank[0])][int(blank[1])] = 1
            else:
              board[int(blank[0])][int(blank[1])] = 2
          else:
            if f_num % 2 == 1: #if odd, play bc smort move
              board[int(blank[0])][int(blank[1])] = 3
            else: #if even, avoid cuz other can play and make it a 4
              board[int(blank[0])][int(blank[1])] = 5

      if row[col] == " ":
        blank = (row_i, col)
        for i in range(1, 4):
          if row[col + 1] == row[col + i] and row[col + 1] != " ":
            in_row += 1
          
           
          if in_row == 3 and float_num(blank) == 0:
            if row[col+1] == 's':
              board[int(blank[0])][int(blank[1])] = 1
            else:
              board[int(blank[0])][int(blank[1])] = 2
            
  #check cols
  for col_i in range(7):
    #checks for random
    if uninterupted((0, col_i)):
      board[0][col_i] = 4
    for row_i in range(5, -1, -1): #starts at row 6, goes up to 0
      in_row = 0
      if board[row_i][col_i]!="s" or board[row_i][col_i]!="o":
        for i in range(1, 3):
          if board[row_i][col_i]==board[row_i - i][col_i]:
            in_row += 1
        if in_row == 3 and board[row_i+3][col_i]==" ":
            board[0][col_i] = check_for
  for r in range(6):
    print(board[r])
 
'''
Checks how much it's floating
'''
def float_num(blank):
  global board
  

  print(type(blank))

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
def uninterupted(blank):
  global board
  b_row = blank[0]
  b_col = blank[1]

  for col in range(b_col+1, 6):
    if board[b_row][col] != ' ' and board[b_row][col] != 's' and  board[b_row][col] != 'o':
      return False
  return True
      


async def gameloop (socket, created):
  active = True
  while active:
    
    message = (await socket.recv()).split(':')
    print(message)

    match message[0]:
      case 'GAMESTART':
        print(created)
        if created == True:
          print("AAAAAA")

          move = 3
          await socket.send(f'PLAY:{move}')
          update_board(move, 's')
          
      case'OPPONENT':
        print(message[1])
        print("AAAAAA")
        move = calculate_move(message[1])
        update_board(move, 's')

        valid = False
        while valid == False:
          for row in range(6):
            if board[row][move]==' ':
              valid = True
          if valid!=True:
            move = random.randint(0, 7)

        print(move)
        await socket.send(f'PLAY:{move}')
        
      case 'WIN' | 'LOSS' | 'DRAW' | 'TERMINATED':
        print(message[0])

      case 'ERROR':
        move = random.randint(0, 7)
        await socket.send(f'PLAY:{move}')

        active = False

async def create_game (server):
  async with websockets.connect(f'ws://{server}/create') as socket:
    await gameloop(socket, True)

async def join_game(server, id):
  async with websockets.connect(f'ws://{server}/join/{id}') as socket:
    await gameloop(socket, False)

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