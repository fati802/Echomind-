import { Outfit, Inter } from "next/font/google";
import "./globals.css";
import AlertBanner from "@/components/AlertBanner";

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata = {
  title: "EchoMind — Your Caring Memory Assistant",
  description: "A private, AI-powered visual memory companion designed to help you remember daily events reassuringly and easily.",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${outfit.variable} ${inter.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-cream text-dark font-sans">
        <div className="px-4 pt-4 max-w-3xl mx-auto w-full">
          <AlertBanner />
        </div>
        {children}
      </body>
    </html>
  );
}