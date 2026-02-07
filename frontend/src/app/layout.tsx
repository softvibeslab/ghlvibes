import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "GoHighLevel Clone - Workflows",
  description: "Automate your business with powerful workflows",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-background">
          {/* Header */}
          <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="container flex h-14 items-center">
              <div className="mr-4 hidden md:flex">
                <a className="mr-6 flex items-center space-x-2" href="/">
                  <span className="hidden font-bold sm:inline-block">
                    GoHighLevel Clone
                  </span>
                </a>
                <nav className="flex items-center space-x-6 text-sm font-medium">
                  <a
                    href="/workflows"
                    className="transition-colors hover:text-foreground/80 text-foreground"
                  >
                    Workflows
                  </a>
                  <a
                    href="/contacts"
                    className="transition-colors hover:text-foreground/80 text-foreground/60"
                  >
                    Contacts
                  </a>
                  <a
                    href="/analytics"
                    className="transition-colors hover:text-foreground/80 text-foreground/60"
                  >
                    Analytics
                  </a>
                </nav>
              </div>
              <div className="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                <nav className="flex items-center">
                  <a
                    href="/settings"
                    className="text-sm font-medium transition-colors hover:text-foreground/80 text-foreground/60"
                  >
                    Settings
                  </a>
                </nav>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="container py-6">{children}</main>
        </div>
        </Providers>
      </body>
    </html>
  );
}
