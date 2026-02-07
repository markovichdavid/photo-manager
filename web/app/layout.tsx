import "./globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "Photo Manager",
  description: "העלאה וניהול תמונות דרך השרת",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="he" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
