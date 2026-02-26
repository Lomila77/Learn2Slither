from src.board import Board
import sys

if __name__ == "__main__":
    #TODO: Take arguments form input or from json
    # try:
        if len(sys.argv) != 1:
            pass
        else:
            env = Board()
    # except Exception as e:
    #     print(e)
    #     sys.exit(1)
