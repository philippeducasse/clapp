import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { ThemeProvider } from "@/components/theme-provider";
import Navbar from "@/components/common/navigation/Navbar";
import { Toaster } from "@/components/ui/sonner";
import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/ui/app-sidebar";
import StoreProvider from "@/redux/StoreProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Circus Agent",
  description: "Your personal assistant for your career in the performance arts",
};

const RootLayout = ({ children }: Readonly<{ children: React.ReactNode }>) => {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased flex min-h-screen flex-col bg-background`}
      >
        <StoreProvider>
          <SidebarProvider>
            <AppSidebar />

            <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
              <div className="container mx-auto flex-grow p-4 sm:p-6 lg:p-8">
                <header className="flex justify-between border-b pb-4">
                  <Navbar />
                </header>
                <main>{children}</main>
              </div>
              <Toaster />
            </ThemeProvider>
          </SidebarProvider>
        </StoreProvider>
      </body>
    </html>
  );
};

export default RootLayout;
