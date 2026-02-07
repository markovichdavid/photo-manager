# Photo Manager

מערכת בסיסית לניהול העלאת תמונות עם מטא־דאטה, צפייה לפי חתכים, וביקורת תמונה בעזרת מודל שפה.

## יכולות עיקריות
- העלאה של תמונה עם פרטי מטא־דאטה (תאריך העלאה, נושא, בעלים, מיקום, מדריך ועוד).
- שליפה לפי פילטרים (טווח תאריכים, נושא, בעלים, מיקום, מדריך).
- ביקורת תמונה בעזרת מודל שפה (LLM) לפי פרמטרים שתקבעו.

## הרצה מהירה
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# הרצה
uvicorn app.main:app --reload
```

## משתני סביבה
העתיקו את `.env.example` לקובץ `.env` כדי להגדיר חיבור ל־LLM.

```bash
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
```

## API עיקריים
- `POST /images` — העלאת תמונה עם מטא־דאטה (multipart/form-data).
- `GET /images` — רשימת תמונות עם פילטרים.
- `GET /images/{image_id}` — פרטי תמונה.
- `GET /images/{image_id}/file` — הורדת קובץ התמונה.
- `POST /images/{image_id}/review` — בקשת ביקורת LLM.

ראו דוגמה לסכמות והחזרה ב־`/docs` של FastAPI.

## אפליקציית ווב (Next.js)
בתיקיית `web/` נמצאת אפליקציית Next.js שמאפשרת להעלות תמונות לשרת ולראות אותן בגלריה.

```bash
cd web
npm install
npm run dev
```

אפשר להגדיר את כתובת ה-API עם המשתנה:
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```
