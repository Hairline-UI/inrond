import type { Metadata, Viewport } from "next";
import { GeistMono } from "geist/font/mono";
import "./globals.css";

const title = "Inrond: Inter, with a roundness axis";
const description =
  "A free variable font that runs from Inter to fully round at every weight, in roman and a drawn italic, without changing a single letter width. 2,937 glyphs, Cyrillic and Greek, SIL Open Font License.";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? "https://inrond.hairlineui.com"),
  title: { absolute: title },
  description,
  openGraph: { type: "website", siteName: "Inrond", title, description, url: "/" },
  twitter: { card: "summary_large_image", title, description },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#ffffff" },
    { media: "(prefers-color-scheme: dark)", color: "#121212" },
  ],
};

// Applies the saved or system theme before first paint, so nobody sees the other theme flash.
const themeScript = `try{var t=localStorage.getItem("theme");var d=t?t==="dark":matchMedia("(prefers-color-scheme: dark)").matches;document.documentElement.classList.add(d?"dark":"light")}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={GeistMono.variable} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
        <link rel="preload" href="/fonts/Inrond.latin.woff2" as="font" type="font/woff2" crossOrigin="anonymous" />
        <link rel="stylesheet" href="/fonts/inrond.css" />
      </head>
      <body>{children}</body>
    </html>
  );
}
