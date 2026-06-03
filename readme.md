# Zambeel Grade Update Notifier 🚀

An automated, serverless tracking engine designed to monitor academic grade releases on the Oracle PeopleSoft-based **Zambeel** portal. This project leverages asynchronous polling via GitHub Actions to provide real-time intelligence on GPA-altering updates.

---

## 🛠 Technical Architecture

The system operates as a headless automated agent. It utilizes a **State-Persistence Model** to minimize unnecessary notifications and redundant processing.

- **Engine:** Python 3.9+ with `Requests` for session persistence and `BeautifulSoup4` for DOM parsing.
- **Automation:** GitHub Actions (Ubuntu-latest) triggered via `cron` and `workflow_dispatch`.
- **State Management:** A local JSON-based cache (`last_grades.json`) tracks the delta between system runs.
- **Security:** AES-256 encrypted GitHub Secrets for credential isolation.

---

## 🏗 System Workflow

1. **Initialization:** The GitHub Actions runner boots an Ubuntu environment and installs the specified Python dependencies.
2. **Authentication:** The script initiates a `requests.Session()` with a spoofed User-Agent to bypass PeopleSoft's bot detection, performing a multi-step handshake to secure an `ICSID` and `ICStateNum`.
3. **Data Extraction:** The agent navigates to the Academic Records component, parses the grade table, and maps Course IDs to their respective Letter Grades.
4. **Differential Analysis:** The current data is compared against `last_grades.json`. 
   - If `Current_Grade != Cached_Grade`, a notification trigger is set.
5. **Persistence & Notification:** If changes are detected, the system dispatches an SMTP alert via Gmail’s SSL relay and commits the new state back to the repository.

---

## ⚙️ Setup & Replication

To deploy this instance on your own infrastructure or GitHub account, follow these technical requirements:

### 1. Repository Secrets Configuration
For the workflow to authenticate against external services, you must configure the following **Repository Secrets** in `Settings > Secrets and variables > Actions`:

| Secret Name | Description |
| :--- | :--- |
| `ZAMBEEL_USER` | Your University Student ID / Portal Username. |
| `ZAMBEEL_PASS` | Your Portal Password (handled as a literal string). |
| `GMAIL_USER` | The sender email address (Must be a Gmail account). |
| `GMAIL_PASS` | A 16-character **App Password** (not your standard account password). |
| `UNI_EMAIL` | The destination address where alerts will be delivered. |

### 2. Workflow Permissions
Since the bot must update the `last_grades.json` file automatically, you must elevate its permissions:
- Navigate to **Settings > Actions > General**.
- Under **Workflow permissions**, select **Read and write permissions**.
- Check the box for **Allow GitHub Actions to create and approve pull requests**.

### 3. The Cron Schedule
The default configuration is optimized for university operating hours to conserve runner minutes:
- **Interval:** Every 30 minutes (`0,30`).
- **Active Hours:** 5:00 AM – 4:30 PM UTC.
- **Manual Trigger:** Enabled via `workflow_dispatch` for on-demand debugging.

---

## 💻 Local Development

To run the agent in a local environment for debugging:

1. **Clone the repository:**
  ```bash
   git clone [https://github.com/your-username/Zambeel-Grade-Update-Notifier.git](https://github.com/your-username/Zambeel-Grade-Update-Notifier.git) ''

2. **Setup Virtual Environment:**
 ```bash
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt ``

3. Environmental Variables:
Create a .env file in the root directory (this is automatically ignored by .gitignore).
⚖️ License
This project is licensed under the MIT License - see the LICENSE file for details.
