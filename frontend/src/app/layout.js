import { Outfit, Inter } from "next/font/google";
import "./globals.css";
import AlertBanner from "@/app/components/AlertBanner";
import Header from "@/app/components/Header";

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
  description:
    "A private, AI-powered visual memory companion designed to help you remember daily events reassuringly and easily.",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${outfit.variable} ${inter.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-cream text-dark font-sans">
        <Header />
        <div className="w-full px-5 sm:px-8 lg:px-12 pt-4">
          <AlertBanner />
        </div>
        <main className="flex-1 flex flex-col w-full">{children}</main>
      </body>
    </html>
  );
}
