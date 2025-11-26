import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/ui/app-sidebar";
import Navbar from "@/components/common/navigation/Navbar";
import StoreProvider from "@/redux/StoreProvider";
import ProfileHydrator from "@/components/ProfileHydrator";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <StoreProvider>
      <ProfileHydrator />
      <SidebarProvider>
        <AppSidebar />
        <div className="container mx-auto flex-grow p-4 sm:p-6 lg:p-8">
          <header className="flex justify-between border-b pb-4 w-full">
            <Navbar />
          </header>
          <main>{children}</main>
        </div>
      </SidebarProvider>
    </StoreProvider>
  );
}
