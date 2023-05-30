from src.utils.download import FileDownloader
import asyncio


def main():
    url = "https://example.com/examplefile.txt"
    destination = "localfile.txt"

    downloader = FileDownloader(url, destination)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(downloader.start_download())
    loop.close()


if __name__ == '__main__':
    main()
