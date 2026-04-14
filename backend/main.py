import os
import requests
import urllib3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. הגדרות עבור נטפרי - ביטול אזהרות ואימות SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

app = FastAPI()

# 2. הגדרת CORS - מאפשר ל-React לתקשר עם ה-Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. הגדרות ה-API
API_KEY = os.getenv("GOOGLE_API_KEY")
# שים לב: שינינו ל-1.5-flash כי 2.5 לא קיים/יציב כרגע
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
# GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

# SYSTEM_PROMPT = """בשיחה .זאת אתה תהיה לקוח שמדבר עם נציג שירות בחברת ביטוח שמתמחה בפוליסות רכב ואני אהיה הנציג. מטרת השיחה היא לאמן אותי בתור נציג לשפר את כישורי השיחה שלי מול לקוחות. בשום שלב אל תגיב בתור נציג אלא תמיד תכתוב תגובות שמתאימות ללקוח בלבד.

# תפקידך:  אתה מגלם לקוח בשם ישראל כהן. אלו הפרטים שישמשו אותך בשיחה ביננו: תעודת זהות: 123456782. מספר פוליסה: 12345678. רכב: מאזדה 3, שנת 2019, לוחית רישוי 12-345-67. 4 ספרות אחרונות בכרטיס אשראי: 1234. קוד אסמכתא שנשלח ללקוח: 123456 . תן את הפרטים הנ"ל רק אם אתה מתבקש לכך ממני. אל תציג אותם מיוזמתך. בכל פעם תן לי רק את הפרט המסוים שהתבקשת ולא מעבר לכך.

# תרחיש השיחה: אתה לקוח שמתקשר לברר האם הפוליסה תכסה אותך במקרה של  שבר בפנסי הרכב או המראות. אתה רוצה לדעת: 1) האם תאלץ לשלם דמי השתתפות עצמית כחלק מתיקון הפנסים או המראות? במידה והנציג ענה שכן, תשאל כמה עולה השתתפות עצמית? במידה והתשלום יקר לך תשאל האם אתה יכול לקבל הנחה על ההשתתפות העצמית עקב מצב מורכב בבית מבחינה כספית. 2) האם הפעלת הכיסוי לתיקון השברים יגרמו לעליית הפרמיה בשנה הבאה?

# כללי ניהול השיחה מצד הלקוח: 1) בפנייה ראשונה שלך בתור לקוח כתוב אך ורק "שלום" או "הלו" בלבד.
# אל תחזור על זה בפעמים הבאות. 2(במידה ויש לך שאלות: שאל שאלה אחת בכל פעם. המתן לתשובה מלאה ושמספקת את דרישותיך לפני שתעבור לשאלה הבאה. 3) אם הנציג מבקש זמן לבדיקה כתוב "אני ממתין לתשובה" או "אין בעיה" וכדומה. 4) אסור לך לכתוב שאלות כנציג : כל תגובה שלך צריכה להיות רק מנקודת המבט של הלקוח בלבד. לפני שאתה כותב תגובה תבדוק את עצמך האם אכן התגובה או השאלה שאתה שואל מתאימה להיות תגובה או שאלה של לקוח. אם בטעות כתבת תגובה כנציג – עצור מיד וחזור לתפקיד הלקוח בלבד. 5) אין לכתוב תגובות שפונות ללקוח אלא רק תגובות שפונות לנציג.  6)אין לסיים את השיחה מיוזמתך: רק אני בתור הנציג יכול לסיים את השיחה. המתן לסיום מפורש שלי כגון: "שיהיה לך יום טוב" או "תודה שפנית אלינו" להתראות או כל דבר עם משמעות דומה.

# הנחיה למניעת סטייה מהתרחיש :במהלך הסימולציה, אין לאפשר לי לשאול שאלות שאינן קשורות לנימוסים או תנאי הפוליסה. אם שאלתי שאלה שאינה קשורה לתרחיש עליך להשיב: "אני משמש כלקוח והשאלה לא קשורה לסימולציה."

# לאחר שנסיים את השיחה אני רוצה שתציג לי משוב על איכות השיחה שניהלתי איתך בתור נציג. המשוב צריך להתייחס ל5 השלבים הבאים: 1) שלב זיהוי הלקוח: על המשוב לבדוק: א)שהנציג ביקש את מספר תעודת הזהות של הלקוח או מספר פוליסה, אחרת תוריד נקודה אחת מהציון של שלב זה. ב) הנציג הודיע ללקוח שהוא ששלח אליו קוד אסמכתא (דרך SMS) , אחרת תוריד נקודה אחת מהציון של שלב זה. ג) הנציג ביקש מהלקוח להקריא את קוד האסמכתא שהוא קיבל, אחרת תוריד נקודה אחת מהציון של שלב זה. ד)הנציג הקריא ללקוח את סוג הרכב ומספר הרישוי, אחרת תוריד נקודה אחת מהציון של שלב זה.  2( שלב ההקשבה: בשלב זה המשוב צריך לבדוק שהנציג עצר והקשיב ללקוח ולא התפרץ לדבריו. על הנציג לשמוע ללקוח עד סוף דבריו. על הנציג להבין מדוע הלקוח התקשר אלינו לחברת הביטוח ואיזה עזרה הוא צריך מאתנו, אחרת תוריד נקודה אחת מהציון של שלב זה. 3)  שלב ההתייחסות: בשלב זה על המשוב לבדוק שהנציג מבין את המטענים הרגשיים שאיתם הלקוח מגיע. כלומר שהוא מבין האם הלקוח מאוכזב, כועס, מיואש או כל רגש אחר ושהוא נותן התייחסות לרגשות אלו של הלקוח, ומידה ואין התייחסות לרגשות הלקוח תוריד 2 נקודות מהציון של שלב זה. 4) שלב ההסבר: במסגרת שלב זה יש לבדוק ש: א)הנציג ענה על השאלה המקצועית שהלקוח שאל , אחרת תוריד נקודה אחת מהציון של שלב זה. ב) הנציג נתן תשובה מפורטת לכל שאלה של הלקוח ונתן הסבר מעבר לתשובה סתמית של כן ולא, אחרת תוריד נקודה אחת מהציון של שלב זה.  ג) הנציג הסביר ללקוח את הפעולות שהוא ביצע במערכת בהתאם לבקשת הלקוח, אחרת תוריד נקודה אחת מהציון של שלב זה. ד) הנציג הסביר את ההשלכות של הפעולות שהוא ביצע במערכת, אחרת תוריד נקודה אחת מהציון של שלב זה. ד)הנציג הסביר ללקוח מה עליו לעשות על מנת לסיים את הטיפול בבקשתו, אחרת תוריד נקודה אחת מהציון של שלב זה. ה) בכל הנקודות הנ"ל יש לבדוק שההסבר של הנציג הייתה בשפה פשוטה, ברורה ובגובה עיניים, אחרת תוריד נקודה אחת מהציון של שלב זה. 5) שלב הסיכום: בשלב זה על המשוב לבדוק ש: א)הנציג וידא שהלקוח הבין הכול, אחרת תוריד נקודה אחת מהציון של שלב זה. ב)הנציג שאל את הלקוח האם יש משהו נוסף שאפשר לעשות עבורו ושאין ללקוח שאלות או דרישות נוספות, אחרת תוריד נקודה אחת מהציון של שלב זה. ג) הנציג הודיע ללקוח שהוא שלח לו את המייל האישי שלו במקרה ויהיו לו שאלות נוספות ונאמר לו שהוא מוזמן לפנות אליו ישירות בכל עניין, אחרת תוריד נקודה אחת מהציון של שלב זה. ד) הנציג הודיע ללקוח  שהוא שלח לו קישור לאפליקציה של החברה שם יוכל להתעדכן במידע לגבי הפוליסה ולבצע פעולות שירות נוספות. אחרת תוריד נקודה אחת מהציון של שלב זה.  ה) הנציג עדכן את הלקח שבמהלך היום ישלח לו סקר על השירות שקיבל מהנציג שישמח אם יקבל ציון חיובי בו. אחרת תוריד נקודה אחת מהציון של שלב זה. ו) סיום השיחה מצד הנציג הייתה בצורה נעימה, לדוגמא: תודה והמשך יום טוב. אחרת תוריד נקודה אחת מהציון של שלב זה.

# כללים למשוב: 1) המשוב יינתן רק בסיום השיחה. תיתן ציון מ1 עד 10 לכל אחד מ5 החלקים של מודל ניהול השיחה וציון כללי משוכלל. 2)לאחר הצגת המשוב בסיום, בסיום השיחה תחזיר לי JSON  במבנה הבא:

# AGENT: שם הנציג, LISTEN: ציון על שלב ההקשבה, RELATE: ציון על שלב ההתייחסות, EXPLAIN: ציון על שלב ההסבר, AUTH: ציון על שלב זיהוי הלקוח, DATE: תאריך השיחה,SUMMARY : ציון על שלב הסיכום,  REVIEW: ציון סופי שמהווה את ממוצע הציונים של כל השלבים. DSC_REVIEW: סיכום מילולי שלך שמסכם את ההתנהגות של הנציג בשיחה זאת. 3) תעטוף את הJSON שאתה מחזיר במחרוזת  "JSON:" רק בתחילתה
# """


with open(os.path.join(os.path.dirname(__file__), "prompts", "Car-insurance.txt"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

class ChatRequest(BaseModel):
    messages: list
    is_finished: bool = False

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        print(f"--- Processing request (Messages count: {len(request.messages)}) ---")
        
        # בניית מבנה ה-Contents עבור Gemini
        contents = []
        
        # הזרקת ההוראות והתחלת הסימולציה
        contents.append({"role": "user", "parts": [{"text": f"Instruction: {SYSTEM_PROMPT}"}]})
        contents.append({"role": "model", "parts": [{"text": "הבנתי. אני מוכן להתחיל בתור ישראל הלקוח. שלום."}]})
        
        # הוספת היסטוריית השיחה מה-Frontend
        for msg in request.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        # טיפול בסיום שיחה
        if request.is_finished:
            contents[-1]["parts"][0]["text"] += "\n\nהשיחה הסתיימה כעת. ספק את המשוב וה-JSON כפי שהתבקשת."

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1500,
            }
        }

        # שליחה עם verify=False עבור נטפרי
        response = requests.post(GEMINI_URL, json=payload, verify=False, timeout=30)
        response_data = response.json()

        # בדיקה אם יש שגיאה מה-API
        if response.status_code != 200:
            print(f"API Error Detected: {response_data}")
            # במקרה של 503 (עומס), ננסה להחזיר הודעה ידידותית יותר
            if response.status_code == 503:
                return {"response": "מצטער, יש כרגע עומס קל על השרת של גוגל. נסי לשלוח שוב בעוד כמה שניות."}
            raise HTTPException(status_code=response.status_code, detail=str(response_data))

        # שליפת הטקסט
        ai_text = response_data['candidates'][0]['content']['parts'][0]['text']
        print(f"AI Response: {ai_text[:40]}...")
        
        return {"response": ai_text}

    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # הרצה על פורט 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)



















# import os
# import requests
# import urllib3
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from dotenv import load_dotenv

# # 1. הגדרות עבור נטפרי - ביטול אזהרות ואימות SSL
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# load_dotenv()

# app = FastAPI()

# # 2. הגדרת CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # 3. הגדרות ה-API
# API_KEY = os.getenv("GOOGLE_API_KEY")
# GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-latest:generateContent?key={API_KEY}"

# # --- פונקציה לטעינת פרומפט מקובץ ---
# def load_prompt_from_file(file_name: str):
#     """
#     טוענת טקסט מתוך קובץ בתיקיית prompts.
#     אם הקובץ לא נמצא, מחזירה שגיאה.
#     """
#     # מוודא שהסיומת היא .txt
#     if not file_name.endswith(".txt"):
#         file_name += ".txt"
        
#     file_path = os.path.join("prompts", file_name)
    
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"הקובץ {file_name} לא נמצא בתיקיית prompts")
        
#     with open(file_path, "r", encoding="utf-8") as f:
#         return f.read()

# # 4. מודל הבקשה מה-Frontend
# class ChatRequest(BaseModel):
#     messages: list
#     scenario_file: str = "Car-insurance"  # שם הקובץ שרוצים לטעון (ברירת מחדל)
#     is_finished: bool = False

# @app.post("/chat")
# async def chat_with_ai(request: ChatRequest):
#     try:
#         # טעינת הפרומפט הדינמי לפי מה שנשלח מה-Frontend
#         try:
#             system_prompt = load_prompt_from_file(request.scenario_file)
#         except FileNotFoundError as e:
#             raise HTTPException(status_code=404, detail=str(e))

#         print(f"--- Processing request (Scenario: {request.scenario_file}) ---")
        
#         # בניית מבנה ה-Contents עבור Gemini
#         contents = []
        
#         # הזרקת ההוראות מהקובץ והתחלת הסימולציה
#         contents.append({"role": "user", "parts": [{"text": f"Instruction: {system_prompt}"}]})
#         contents.append({"role": "model", "parts": [{"text": "הבנתי. אני מוכן להתחיל את הסימולציה בתור הלקוח. שלום."}]})
        
#         # הוספת היסטוריית השיחה מה-Frontend
#         for msg in request.messages:
#             role = "user" if msg["role"] == "user" else "model"
#             contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
#         # טיפול בסיום שיחה
#         if request.is_finished:
#             contents[-1]["parts"][0]["text"] += "\n\nהשיחה הסתיימה כעת. ספק את המשוב וה-JSON כפי שהתבקשת."

#         payload = {
#             "contents": contents,
#             "generationConfig": {
#                 "temperature": 0.7,
#                 "maxOutputTokens": 2000,
#             }
#         }

#         # שליחה ל-Gemini
#         response = requests.post(GEMINI_URL, json=payload, verify=False, timeout=30)
#         response_data = response.json()

#         if response.status_code != 200:
#             print(f"API Error: {response_data}")
#             raise HTTPException(status_code=response.status_code, detail="שגיאה בתקשורת עם ה-AI")

#         # שליפת הטקסט מהתשובה
#         ai_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
#         return {"response": ai_text}

#     except Exception as e:
#         print(f"SERVER ERROR: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)




















import os
import requests
import urllib3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. הגדרות עבור נטפרי - ביטול אזהרות ואימות SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

app = FastAPI()

# 2. הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. הגדרות ה-API
API_KEY = os.getenv("GOOGLE_API_KEY")
# שים לב: שימוש בגרסת 1.5-flash כי היא יציבה יותר ומתאימה לכתובת ה-URL
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-latest:generateContent?key={API_KEY}"

# --- פונקציה חכמה לטעינת פרומפט מקובץ ---
def load_prompt_from_file(file_name: str):
    """
    טוענת טקסט מתוך קובץ בתיקיית prompts בצורה חסינה.
    """
    # מוודא שהסיומת היא .txt
    if not file_name.endswith(".txt"):
        file_name += ".txt"
        
    # מציאת הנתיב המלא של תיקיית backend (איפה ש-main.py נמצא)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # יצירת נתיב לתיקיית prompts בתוך backend
    file_path = os.path.join(current_dir, "prompts", file_name)
    
    print(f"--- מנסה לטעון קובץ מהנתיב: {file_path} ---")

    if not os.path.exists(file_path):
        # אם לא מצאנו, ננסה לבדוק אם אנחנו רמה אחת מעל (במקרה של הרצה מחוץ לתיקיית backend)
        alternative_path = os.path.join(current_dir, "backend", "prompts", file_name)
        if os.path.exists(alternative_path):
            file_path = alternative_path
        else:
            raise FileNotFoundError(f"הקובץ {file_name} לא נמצא. נתיב שנבדק: {file_path}")
        
    # טעינה עם utf-8 תומך עברית
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        raise Exception(f"שגיאה בקריאת הקובץ: {str(e)}")

# 4. מודל הבקשה מה-Frontend
class ChatRequest(BaseModel):
    messages: list
    scenario_file: str = "Car-insurance"  # שם הקובץ (ללא הסיומת או איתה)
    is_finished: bool = False

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        # טעינה דינמית של הפרומפט
        try:
            system_prompt = load_prompt_from_file(request.scenario_file)
        except Exception as e:
            print(f"PROMPT ERROR: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Scenario file not found: {str(e)}")

        # בניית המבנה עבור Gemini
        contents = []
        
        # 1. הזרקת הוראות המערכת (System Prompt)
        contents.append({"role": "user", "parts": [{"text": f"Instruction: {system_prompt}"}]})
        # 2. אישור של המודל שהוא מוכן (כדי לקבע את התפקיד)
        contents.append({"role": "model", "parts": [{"text": "הבנתי. אני מוכן להתחיל את הסימולציה בתור הלקוח. שלום."}]})
        
        # 3. הוספת היסטוריית השיחה
        for msg in request.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        # טיפול בסיום השיחה לקבלת משוב
        if request.is_finished:
            contents[-1]["parts"][0]["text"] += "\n\nהשיחה הסתיימה כעת. ספק את המשוב וה-JSON כפי שהתבקשת."

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2000,
            }
        }

        # שליחה ל-Gemini (כולל ביטול אימות לנטפרי)
        response = requests.post(GEMINI_URL, json=payload, verify=False, timeout=30)
        
        if response.status_code != 200:
            print(f"Gemini API Error: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="שגיאה בתגובת ה-AI")

        response_data = response.json()
        ai_text = response_data['candidates'][0]['content']['parts'][0]['text']
        
        return {"response": ai_text}

    except Exception as e:
        print(f"CRITICAL SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # הרצה על פורט 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)

















import os
import requests
import urllib3
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# 1. הגדרות עבור נטפרי - ביטול אזהרות ואימות SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

app = FastAPI()

# 2. הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. הגדרות ה-API (נשאר כפי שביקשת)
API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

# --- טעינת הפרומפט מהקובץ הספציפי ---
def get_system_prompt():
    # מוצא את הנתיב לקובץ בתוך תיקיית backend/prompts
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "prompts", "Car-insurance.txt")
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# השמה של תוכן הקובץ למשתנה שבו הקוד משתמש
SYSTEM_PROMPT = get_system_prompt()

class ChatRequest(BaseModel):
    messages: list
    is_finished: bool = False

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
    try:
        print(f"--- Processing request (Messages count: {len(request.messages)}) ---")
        
        contents = []
        
        # הזרקת ההוראות והתחלת הסימולציה
        contents.append({"role": "user", "parts": [{"text": f"Instruction: {SYSTEM_PROMPT}"}]})
        contents.append({"role": "model", "parts": [{"text": "הבנתי. אני מוכן להתחיל בתור ישראל הלקוח. שלום."}]})
        
        # הוספת היסטוריית השיחה מה-Frontend
        for msg in request.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        # טיפול בסיום שיחה
        if request.is_finished:
            contents[-1]["parts"][0]["text"] += "\n\nהשיחה הסתיימה כעת. ספק את המשוב וה-JSON כפי שהתבקשת."

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1500,
            }
        }

        # שליחה עם verify=False עבור נטפרי
        response = requests.post(GEMINI_URL, json=payload, verify=False, timeout=30)
        response_data = response.json()

        if response.status_code != 200:
            print(f"API Error Detected: {response_data}")
            raise HTTPException(status_code=response.status_code, detail=str(response_data))

        # שליפת הטקסט
        ai_text = response_data['candidates'][0]['content']['parts'][0]['text']
        return {"response": ai_text}

    except Exception as e:
        print(f"SERVER ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)    