import asyncio
import websockets

async def calculation():
  pass

async def calculate_move(message):
  
  await asyncio.sleep(3)
  
'''
Updates the board given the collumn played, the player ('s' or 'o'), 
and the board array. Returns board with recalculated weights.
'''
async def update_board(col, player, board):
  for i in range(6):
    if board[i][col]!='s' and board[i][col]!='o':
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
3: making this move will result in making an opponent win possible
'''
async def recalculate_weight(board):
  pass
      

async def gameloop (socket, created):
  active = True

  while active:
    message = (await socket.recv()).split(':')

    match message[0]:
      case 'GAMESTART' | 'OPPONENT':
        col = col = calculate_move(message[1])

        await socket.send(f'PLAY:{col}')
      case 'WIN' | 'LOSS' | 'DRAW' | 'TERMINATED':
        print(message[0])

        active = False

async def create_game (server):
  async with websockets.connect(f'ws://{server}/create') as socket:
    await gameloop(socket, True)

async def join_game(server, id):
  async with websockets.connect(f'ws://{server}/join/{id}') as socket:
    await gameloop(socket, False)

if __name__ == '__main__':
  server = input('Server IP: ').strip()

  board = [[" " for _ in range(7)] for _ in range(6)]

  protocol = input('Join game or create game? (j/c): ').strip()

  match protocol:
    case 'c':
      asyncio.run(create_game(server))
    case 'j':
      id = input('Game ID: ').strip()

      asyncio.run(join_game(server, id))
    case _:
      print('Invalid protocol!')