import "./globals.css";

export const metadata = {
  title: "AI ROI Tracker — Feature-Level Cost & Value Analytics",
  description:
    "Track AI feature costs, measure user impact, and optimize ROI with real-time analytics and intelligent model recommendations.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
