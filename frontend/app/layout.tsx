import type { Metadata } from "next";
import { DeployGuard } from "@/components/deploy-guard";
import { BUILD_ID } from "@/lib/build";
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
      <body data-build-id={BUILD_ID}>
        <DeployGuard />
        {children}
      </body>
    </html>
  );
}
