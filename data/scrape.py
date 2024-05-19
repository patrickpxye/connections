import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Configure Chrome options
options = Options()
options.add_argument(
    "--window-size=1920,1080"
)  # Optional: if running headless, define window size
options.headless = True  # Optional: if you want to run Chrome in headless mode

# Enabling browser logs
options.set_capability(
    "goog:loggingPrefs", {"browser": "ALL"}
)  # This is the correct way to enable logging

# List of websites to visit
websites = [
    "https://connections.swellgarfo.com/nyt/1",
    "https://connections.swellgarfo.com/nyt/2",
]

# Initialize the WebDriver
driver = webdriver.Safari()

# Inject JavaScript to override console.log to capture objects
script_to_inject = """
(function() {
    var oldLog = console.log;
    console.log = function(message) {
        if (typeof message === 'object') {
            message = JSON.stringify(message, null, 2);  // Serialize the object
        }
        oldLog.apply(console, [message]);
    };
})();
"""


# Function to fetch console logs
def fetch_console_logs():
    # Retrieve console log entries
    logs = driver.get_log("browser")
    return logs


# Visit websites and capture logs
for site in websites:
    driver.get(site)
    result = driver.execute_script(
        script_to_inject
    )  # Inject the script right after the page load
    print("Injection result", result)
    time.sleep(2)  # Wait for 2 seconds for the page and its scripts to load
    console_logs = fetch_console_logs()

    print(console_logs)

    # Save logs to a file
    with open(
        f"logs_for_{site.replace('http://', '').replace('/', '_')}.txt", "w"
    ) as file:
        for log in console_logs:
            file.write(f"{log['level']} - {log['message']}\n")

# Clean up
driver.quit()

print("Logs have been captured and saved.")
