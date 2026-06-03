import requests
from bs4 import BeautifulSoup
import json
import smtplib
import schedule
import time
from dotenv import load_dotenv
from email.mime.text import MIMEText
import os
load_dotenv()
ZAMBEEL_USER = os.getenv("ZAMBEEL_USER")
ZAMBEEL_PASS = os.getenv("ZAMBEEL_PASS")
GMAIL_USER   = os.getenv("GMAIL_USER")
GMAIL_PASS   = os.getenv("GMAIL_PASS")
GRADES_FILE  ="last_grades.json"
UNI_EMAIL = os.getenv("UNI_EMAIL")
EMP_ID = 30339
BASE_URL = "https://zambeel.lums.edu.pk"

def login():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })

    login_page = session.get(f"{BASE_URL}/psp/ps/?cmd=login")
    
    # Submit login
    login_data = {
        "userid": ZAMBEEL_USER,
        "pwd":    ZAMBEEL_PASS,
        "Submit": "Sign In"
    }
    resp = session.post(
        f"{BASE_URL}/psp/ps/?cmd=login",
        data=login_data,
        allow_redirects=True
    )
    
    if "Sign out" in resp.text or ZAMBEEL_USER in resp.text:
        print("Login successful")
        return session
    else:
        print("Login failed — check credentials")
        return None

def get_term_selection_state(session):
    """Load the term selection page and extract ICStateNum and ICSID"""
    resp = session.get(
        f"{BASE_URL}/psc/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_GRADE.GBL"
    )
    soup = BeautifulSoup(resp.text, "html.parser")
    
    state_num = soup.find("input", {"id": "ICStateNum"})["value"]
    icsid      = soup.find("input", {"id": "ICSID"})["value"]
    
    return state_num, icsid

def fetch_grades_xml(session, state_num, icsid, strm="2502"):
    """POST to grades component and get XML response, change strm according to the session required"""
    
    post_data = {
        "ICType":               "Panel",
        "ICElementNum":         "0",
        "ICStateNum":           state_num,
        "ICAction":             "DERIVED_SSS_SCT_SSR_PB_GO",
        "ICModelCancel":        "0",
        "ICXPos":               "0",
        "ICYPos":               "0",
        "ResponsetoDiffFrame":  "-1",
        "TargetFrameName":      "None",
        "FacetPath":            "None",
        "ICFocus":              "",
        "ICSaveWarningFilter":  "0",
        "ICChanged":            "-1",
        "ICSkipPending":        "0",
        "ICAutoSave":           "0",
        "ICResubmit":           "0",
        "ICSID":                icsid,
        "ICAGTarget":           "true",
        "ICActionPrompt":       "false",
        "ICTypeAheadID":        "",
        "ICBcDomData":          "",
        "ICPanelHelpUrl":       "",
        "ICPanelName":          "",
        "ICFind":               "",
        "ICAddCount":           "",
        "ICAppClsData":         "",
        # Select first term (row 0), change according to your need, 
        "SSR_DUMMY_RECV1$sels$0": "0",
        "ACAD_CAREER":          "UGDS",
        "EMPLID":               EMP_ID,
        "INSTITUTION":          "LUMS",
        "STRM":                 strm,
    }
    
    resp = session.post(
        f"{BASE_URL}/psc/ps/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.SSR_SSENRL_GRADE.GBL",
        data=post_data,
        headers={"X-Requested-With": "XMLHttpRequest"}
    )
    
    return resp.text

def parse_grades_from_xml(xml_text):
    soup = BeautifulSoup(xml_text, "html.parser")
    grades = {}

    print("DEBUG: Starting parse...")
    i = 0
    while True:
        course_el = soup.find("a", {"id": f"CLS_LINK${i}"})
        if not course_el:
            if i == 0:
                print("DEBUG: No courses found at all. Check the HTML IDs.")
            break
            
        grade_el = soup.find("span", {"id": f"STDNT_ENRL_SSV1_CRSE_GRADE_OFF${i}"})
        desc_el  = soup.find("span", {"id": f"CLASS_TBL_VW_DESCR${i}"})
        
        course_code = course_el.get_text(strip=True)
        grade_val   = grade_el.get_text(strip=True).replace('\xa0', '') if grade_el else ""
        description = desc_el.get_text(strip=True) if desc_el else ""
        
        grades[course_code] = {"grade": grade_val, "description": description}
        
        print(f"  [+] Found {course_code}: {grade_val if grade_val else 'Pending'}")
        i += 1
    
    print(f"DEBUG: Successfully parsed {len(grades)} courses.")
    return grades

def send_notification(changes):
    body = "Grade update detected on Zambeel:\n\n"
    for course, info in changes.items():
        old = info.get("old", "N/A")
        new = info.get("new", "N/A")
        body += f"{course} ({info.get('desc','')}): {old} → {new}\n"
    
    msg = MIMEText(body)
    msg["Subject"] = "Zambeel Grade Update Notification"
    msg["From"]    = GMAIL_USER
    msg["To"]      = UNI_EMAIL
    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_USER, GMAIL_PASS)
        s.send_message(msg)
    print("Email sent.")

def check_grades():
    session = login()
    if not session: return
    
    state_num, icsid = get_term_selection_state(session)
    response_text = fetch_grades_xml(session, state_num, icsid, strm="2502")
    
    # SAVE TO FILE
    # with open("debug_output.html", "w", encoding="utf-8") as f:
    #     f.write(response_text)
    # print("Response saved to debug_output.html. Open this in your browser!")
    try:
        with open(GRADES_FILE, "r") as f:
            previous = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        previous = {}
    current = parse_grades_from_xml(response_text)
    print(f"Current grades: {current}")
    
    changes = {}
    for course, data in current.items():
        old_grade = previous.get(course, {}).get("grade", "")
        new_grade = data["grade"]
        if new_grade and new_grade != old_grade:
            changes[course] = {
                "old": old_grade if old_grade else "Pending",
                "new": new_grade,
                "desc": data["description"]
            }
            
    if changes:
        print(f"Changes: {changes}")
        send_notification(changes)
    else:
        print("No new grades.")
    
    with open(GRADES_FILE, "w") as f:
        json.dump(current, f, indent=2)

# scheduling is now done through github actions
# schedule.every(30).minutes.do(check_grades)
check_grades()  # Run immediately on start

# while True:
#     schedule.run_pending()
#     time.sleep(60)