from src.board import Board
import sys
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="Snake game options")

    parser.add_argument(
        "--mode", type=str, choices=["training", "manuel", "ai_player"],
        default="training", help="Game mode")
    parser.add_argument(
        "--map_shape", type=int, nargs=2, default=[10, 10],
        help="Map size: height width")

    parser.add_argument("--save", action="store_true", help="Save training")
    parser.add_argument(
        "--save_as", type=str, default="experiments_00",
        help="Save as filename")
    parser.add_argument(
        "--save_in", type=str,
        default="/home/gcolomer/Documents/Learn2Slither/save",
        help="Directory to save")

    parser.add_argument(
        "--load_checkpoint", action="store_true", help="Load checkpoint")
    parser.add_argument(
        "--load_data_from", type=str, default="",
        help="Data file to load checkpoint")
    parser.add_argument(
        "--load_weights_from", type=str, default="",
        help="Weights file to load checkpoint")

    parser.add_argument("--epochs", type=int, default=1000)
    parser.add_argument("--learning_rate", type=float, default=0.9)
    parser.add_argument("--epsilon_greedy", type=float, default=0.1)
    parser.add_argument(
        "--force_exploration", action="store_true", help="Force exploration")
    parser.add_argument(
        "--step_by_step", action="store_true", help="Play step by step")

    parser.add_argument(
        "--interface", action="store_true", help="Enable interface")
    parser.add_argument(
        "--terminal", action="store_true", help="Enable terminal display")
    parser.add_argument("--cell_size", type=int, default=40)
    parser.add_argument("--framerate", type=int, default=60)
    parser.add_argument("--interface_speed", type=int, default=200)
    parser.add_argument("--terminal_speed", type=int, default=75)

    args = parser.parse_args()
    return args


def main():
    try:
        if len(sys.argv) != 1:
            args = parse_arguments()
            Board(**vars(args))
        else:
            Board()
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
