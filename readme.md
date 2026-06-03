# Zambeel Grade Update Notifier 🚀

An automated tracking system that monitors academic grade releases on the Oracle PeopleSoft-based **Zambeel** portal. It runs on GitHub Actions, polls for grade changes every 30 minutes, and sends an email notification the moment a grade is posted.

---

## 🛠 Technical Architecture

The system operates as a headless automated agent using a **State-Persistence Model** to avoid redundant notifications.

- **Engine:** Python 3.9+ with `Requests` for session management and `BeautifulSoup4` for HTML/XML parsing.
- **Automation:** GitHub Actions (Ubuntu-latest) triggered via `cron` and `workflow_dispatch`.
- **State Management:** A JSON cache (`last_grades.json`) persists grade state between runs and is committed back to the repo after each check.
- **Security:** GitHub Environment Secrets for credential isolation.

---

## 🏗 System Workflow

1. **Initialization:** The GitHub Actions runner boots an Ubuntu environment and installs Python dependencies.
2. **Authentication:** The script initiates a `requests.Session()`, retrieves the CSRF token from the login page, and performs a credential POST to obtain a valid `PS_TOKEN` session cookie.
3. **State Extraction:** The authenticated session navigates to the grades component, extracts `ICStateNum` and `ICSID` from the page, then POSTs to the grades endpoint which returns structured XML containing course and grade data.
4. **Parsing:** Course IDs and letter grades are extracted from the XML response by targeting stable PeopleSoft element IDs.
5. **Differential Analysis:** Current grades are compared against `last_grades.json`.
   - If `current_grade != cached_grade`, a notification is triggered.
6. **Notification & Persistence:** If changes are detected, an SMTP alert is dispatched via Gmail SSL and the updated state is committed back to the repository.

---

## ⚙️ Setup & Replication

### 1. GitHub Environment & Secrets

Go to **Settings > Environments** and create a new environment named exactly `grade notifier`. Inside that environment, add the following secrets:

| Secret Name | Description |
| :--- | :--- |
| `ZAMBEEL_USER` | Your university student ID / portal username |
| `ZAMBEEL_PASS` | Your portal password |
| `GMAIL_USER` | Sender Gmail address |
| `GMAIL_PASS` | 16-character Gmail App Password (not your account password) |
| `UNI_EMAIL` | Destination address for grade alerts |
| `EMP_ID` | Your Zambeel Employee  ID |

> **Note:** Gmail App Passwords require 2-Step Verification to be enabled on your Google account. Generate one at Google Account > Security > App Passwords.

### 2. Workflow Permissions

The bot commits updated grade state back to the repo after each run. Two ways to enable this:

**Option A — Repo-wide setting:**
- Go to **Settings > Actions > General**
- Under **Workflow permissions**, select **Read and write permissions**

**Option B — Already handled in the YAML** via:
```yaml
permissions:
  contents: write
```

### 3. Cron Schedule

The default schedule polls every 30 minutes during Pakistan daytime hours:

- **Interval:** Every 30 minutes
- **Active Hours:** 10:00 AM – 9:30 PM PKT (05:00–16:30 UTC)
- **Manual Trigger:** Available via `workflow_dispatch` for on-demand runs

To change the schedule, edit the cron expression in `.github/workflows/grade-notifier.yml`:
```yaml
- cron: '0,30 5-16 * * *'
```

---

## 💻 Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/Zambeel-Grade-Update-Notifier.git
cd Zambeel-Grade-Update-Notifier
```

2. **Set up a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

3. **Create a `.env` file** in the root directory:
```env
ZAMBEEL_USER=your_student_id
ZAMBEEL_PASS=your_password
GMAIL_USER=your@gmail.com
GMAIL_PASS=your_app_password
UNI_EMAIL=destination@lums.edu.pk
EMP_ID=your_student_id
```

> The `.env` file is listed in `.gitignore` and will never be committed.

4. **Run locally:**
```bash
python script.py
```

---

## 📁 Project Structure

```
Zambeel-Grade-Update-Notifier/
├── .github/
│   └── workflows/
│       └── grade-notifier.yml   # GitHub Actions workflow
├── script.py                    # Main polling and notification script
├── last_grades.json             # Persisted grade state (auto-updated)
├── .env                         # Local credentials (gitignored)
├── .gitignore
└── README.md
```

---

## ⚖️ License

This project is licensed under the MIT License — see the LICENSE file for details.
