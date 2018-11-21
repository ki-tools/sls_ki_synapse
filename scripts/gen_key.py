#!/usr/bin/env python3
import secrets
import argparse

def main():
    """
    Generates a random key.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('bytes', type=int, nargs='?', help='How many bytes to generate.', default=64)
    args = parser.parse_args()

    print(secrets.token_hex(args.bytes))


if __name__ == "__main__":
    main()
