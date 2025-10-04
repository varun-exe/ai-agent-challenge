import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    print(f"Target bank: {args.target}")

if __name__ == "__main__":
    main()
