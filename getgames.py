import chess.pgn
import re
import requests
from datetime import datetime, timezone

#,'Inaccuracy'
username='my_username'
last_n_days=30
mistake_types=['Blunder','Mistake']
dl_games=True
games_pgn_loc="my_game_loc.pgn"
out_pgn_loc="my_tactics_loc.pgn"

if dl_games:
    utc_cutoff=str(round(datetime.now(timezone.utc).timestamp() * 1000) -last_n_days*60*60*24*1000) 
    response = requests.get('https://lichess.org/api/games/user/'+username+'?since='+utc_cutoff+'&analysed=true&perfType="blitz"&rated=true&literate=true&pgnInJson=true&evals=true')
    with open(games_pgn_loc, "wb") as f:
        f.write(response.content)


pgn = open(games_pgn_loc)
positions = []
while True:
    first_game = chess.pgn.read_game(pgn)

    if first_game is None:
        break

    if first_game.headers['Black']==username:
        player_side=True
    else:
        player_side=False

    board = first_game.board()
    for node in first_game.mainline():
        print(node.comment)
        comment = node.comment
        if any(x in comment for x in mistake_types) and player_side==node.turn():
            match = re.search(r'(Blunder|Mistake|Inaccuracy)\.\s+([a-zA-z0-9+-]+)\s+was best', comment)
            mistake_type = 'Blunder' if 'Blunder' in comment else 'Mistake' if 'Mistake' in comment else 'Inaccuracy'
            best_move = match.group(2) if match else "Unknown"
            positions.append({
            'fen': board.fen(),
            'best_move': best_move,
            'original_move': board.san(node.move),
            'full_comment': comment,
            'mistake_type':mistake_type,
            'headers':first_game.headers,
            'player_side':player_side
            })
            print(f"FEN: {board.fen()}")

        board.push(node.move)
        

with open(out_pgn_loc, 'w') as output_file:
    for pos in positions:
        game = chess.pgn.Game()
        game.headers=pos['headers']
        game.headers["FEN"] = pos['fen']
        game.comment = f"Original move was: {pos['original_move']} ({pos['mistake_type']})"

        print(game, file=output_file)
        if pos['player_side']:
            print(f"1. ... {pos['best_move']}" +" {"+f"{pos['original_move']} is a {pos['full_comment']}"+"}", file=output_file) 
        else:
            print(f"1. {pos['best_move']}" +" {"+f"{pos['original_move']} is a {pos['full_comment']}"+"}", file=output_file)  
        print("\n", file=output_file)  # Add blank line between games



