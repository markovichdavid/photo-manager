"use client";

import { useEffect, useMemo, useState } from "react";

type ImageRecord = {
  id: number;
  filename: string;
  subject?: string | null;
  owner_name?: string | null;
  location?: string | null;
  guide_name?: string | null;
  notes?: string | null;
  uploaded_at?: string | null;
};

const emptyForm = {
  subject: "",
  owner_name: "",
  location: "",
  guide_name: "",
  notes: "",
};

export default function HomePage() {
  const [images, setImages] = useState<ImageRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [form, setForm] = useState(emptyForm);

  const apiBase = useMemo(
    () =>
      process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ||
      "http://localhost:8000",
    []
  );

  const loadImages = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiBase}/images`, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("לא ניתן לטעון תמונות");
      }
      const data = (await response.json()) as ImageRecord[];
      setImages(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "שגיאה לא ידועה");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadImages();
  }, [apiBase]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError("יש לבחור קובץ תמונה לפני השליחה");
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      Object.entries(form).forEach(([key, value]) => {
        if (value) {
          formData.append(key, value);
        }
      });

      const response = await fetch(`${apiBase}/images`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail || "ההעלאה נכשלה");
      }

      setForm(emptyForm);
      setFile(null);
      await loadImages();
    } catch (err) {
      setError(err instanceof Error ? err.message : "שגיאה לא ידועה");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main>
      <header>
        <div>
          <h1>Photo Manager</h1>
          <p>העלאת תמונות לשרת וצפייה בגלריה.</p>
        </div>
        <span className="badge">Next.js + FastAPI</span>
      </header>

      <section className="section">
        <h2>העלאת תמונה חדשה</h2>
        <form onSubmit={handleSubmit}>
          <label>
            קובץ תמונה
            <input
              type="file"
              accept="image/*"
              onChange={(event) => setFile(event.target.files?.[0] || null)}
            />
          </label>

          <div className="grid">
            <label>
              נושא
              <input
                type="text"
                value={form.subject}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    subject: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              בעלים
              <input
                type="text"
                value={form.owner_name}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    owner_name: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              מיקום
              <input
                type="text"
                value={form.location}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    location: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              מדריך
              <input
                type="text"
                value={form.guide_name}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    guide_name: event.target.value,
                  }))
                }
              />
            </label>
          </div>

          <label>
            הערות
            <textarea
              rows={3}
              value={form.notes}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  notes: event.target.value,
                }))
              }
            />
          </label>

          <button type="submit" disabled={submitting}>
            {submitting ? "מעלה..." : "שליחה"}
          </button>

          {error && <div className="notice">{error}</div>}
        </form>
      </section>

      <section className="section">
        <h2>גלריה</h2>
        {loading ? (
          <p>טוען תמונות...</p>
        ) : images.length === 0 ? (
          <p>אין עדיין תמונות. העלו תמונה ראשונה כדי להתחיל.</p>
        ) : (
          <div className="gallery">
            {images.map((image) => (
              <article className="card" key={image.id}>
                <img
                  src={`${apiBase}/images/${image.id}/file`}
                  alt={image.subject || image.filename}
                  loading="lazy"
                />
                <strong>{image.subject || image.filename}</strong>
                <div className="meta">{image.owner_name || "ללא בעלים"}</div>
                <div className="meta">{image.location || "ללא מיקום"}</div>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
