import aiohttp
import asyncio


class FileDownloader:
    def __init__(self, url, destination):
        self.url = url
        self.destination = destination

    async def download_file(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                if response.status == 200:
                    with open(self.destination, 'wb') as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)
                    print(f"Download complete: {self.destination}")
                else:
                    print(f"Failed to download file from {self.url}")

    async def start_download(self):
        await self.download_file()


# Example usage:
if __name__ == '__main__':
    url = "https://example.com/examplefile.txt"
    destination = "localfile.txt"

    downloader = FileDownloader(url, destination)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(downloader.start_download())
    loop.close()