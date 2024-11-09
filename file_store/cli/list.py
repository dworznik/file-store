# my_cli_tool/main.py
import argparse
from file_store.db import Database
from datetime import datetime


def main():
    with Database() as db:
        rows = db.fetch_file_events()
        for row in rows:
            print(
                f"ID: {row.id}, File Name: {row.file_name}, Uploaded At: {row.uploaded_at}"
            )


def run():
    parser = argparse.ArgumentParser(description="List Events CLI Tool")
    args = parser.parse_args()
    main()


if __name__ == "__main__":
    run()
