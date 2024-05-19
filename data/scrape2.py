import asyncio
import json
from pyppeteer import launch


async def capture_logs(url):
    # Start the browser and open a new page
    browser = await launch(headless=True)
    page = await browser.newPage()

    logs = []  # List to store logs for this page

    # Define the console event handler
    page.on("console", lambda msg: logs.append(msg.text))

    # Navigate to the URL
    await page.goto(url)

    # Inject JavaScript to override console.log
    await page.evaluate(
        """() => {
        const originalLog = console.log;
        console.log = function(...args) {
            originalLog(...args.map(arg => {
                return (typeof arg === 'object') ? JSON.stringify(arg) : arg;
            }));
        };
    }"""
    )

    # Wait for a few seconds to capture logs
    await asyncio.sleep(0.5)  # Adjust sleep time as necessary

    # Close the browser
    await browser.close()

    return logs[-1]


async def main():
    urls = [
        f"https://connections.swellgarfo.com/nyt/{i}"
        for i in range(1, 343)  # up to 5/18
    ]  # List of URLs

    logs_dict = {}
    for idx, url in enumerate(urls):
        print(url)
        result = await capture_logs(url)
        print(result)
        try:
            logs_dict[idx + 1] = json.loads(result)
        except:
            result = await capture_logs(url)
            logs_dict[idx + 1] = json.loads(result)

    # Save to a JSON file
    with open("connections.json", "w") as f:
        json.dump(logs_dict, f, indent=4)


# Run the asyncio event loop
asyncio.get_event_loop().run_until_complete(main())
