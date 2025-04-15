<h1 align="center">
  <br>
  <a href="https://github.com/manojxshrestha/">
    <img src="https://github.com/user-attachments/assets/c10a85ca-c97e-4fdf-af29-b4ebf59bcc8b" alt="dorkpwn" width="600">
  </a>
  <br>
  dorkpwn
  <br>
</h1>

<h4 align="center">A Powerful URL Discovery Toolkit</h4>

dorkpwn is a Python-based tool designed to automate Google dorking (using DuckDuckGo) to discover potentially sensitive or exposed URLs on a target website. It leverages search engine queries (dorks) to find pages, filters live URLs using the httpx tool, and provides options for proxy support, logging, and saving results.

Note: `This tool is intended for authorized security testing and research purposes only. Unauthorized use may violate laws or terms of service. Always obtain permission before scanning any target.`

## Features
- Search for live URLs using dorks on DuckDuckGo.
- Filter live URLs with `httpx` (supports HTTP status codes 200, 301, 302, 403, 401).
- Customizable number of results (`all` or a specific number).
- Optional proxy support for anonymity.
- Save results to a file.
- Logging for debugging and tracking.
- Random delays to avoid rate-limiting.

## Prerequisites
Before using dorkpwn, ensure you have the following installed:

### System Dependencies
- **Python 3.6+**: The script uses Python 3.
- **httpx**: A command-line tool to filter live URLs. Install it via:
  ```
  go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
  ```
  Ensure `httpx` is in your system PATH.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/manojxshrestha/dorkpwn.git
   cd dorkpwn
   ```
2. Set up a Python virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
     ```
     source venv/bin/activate
     ```
   Once activated, you should see `(venv)` in your terminal prompt.
4. Install the Python dependencies in the virtual environment:
   ```
   pip install requests beautifulsoup4 fake-useragent urllib3
   ```
5. Prepare your `dorks.txt` file with the dork queries you want to use, or you can use the tool's default `dorks.txt` file.

## Usage
With the virtual environment activated, run the script and follow the interactive prompts:
```
python3 dorkpwn.py
```

### Prompts
- **Target site**: Enter the target site (e.g., `example.com`). Leave blank to search without a specific site.
- **Dorks file**: Specify the path to your dorks file (e.g., `dorks.txt`).
- **Number of results**: Enter a number or `all` to fetch all possible results.
- **Save output**: Choose `Y` to save results to a file, then specify the filename (e.g., `results.txt`).
- **Proxy URL**: Enter a proxy URL (e.g., `http://proxy:port`) or leave blank for none.

### Example
```
[+] Enter The Target site: example.com
[+] Enter The Dorks file (e.g., dorks.txt): dorks.txt
[+] Enter Total Number of Results You Want (or type 'all' to fetch everything): all
[+] Do You Want to Save the Output? (Y/N): Y
[+] Enter Output Filename (e.g., results.txt): results.txt
[+] Enter Proxy URL (e.g., http://proxy:port, leave empty for none): 
```

## Output
- Live URLs are printed to the console in green.
- If saving is enabled, results are written to the specified file (e.g., `results.txt`).
- Logs are saved to `dorking.log` for debugging.

## Notes
- The script uses DuckDuckGo's HTML search endpoint for querying.
- Rate-limiting is handled with retries and exponential backoff.
- Random delays are added between searches to avoid being blocked.
- Temporary files are created and deleted during URL filtering.
