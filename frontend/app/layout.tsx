import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "DotaReframe",
  description: "Post-match Dota 2 review that turns one match into one clear fix"
};

export default function RootLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
