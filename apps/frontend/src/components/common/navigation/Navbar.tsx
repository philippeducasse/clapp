"use client";

import { DarkModeToggle } from "@/components/ui/dark-mode-toggle";
import Breadcrumbs from "./breadcrumbs/Breadcrumbs";
import { UserRound, LogOut, Bell } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { AlertModal } from "../modals/AlertModal";
import { useState } from "react";
import { useSelector } from "react-redux";
import { profileApiService } from "@/api/profileApiService";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { selectUnreadReminderCount } from "@/redux/slices/reminderSlice";
const Navbar = () => {
  const confirmLogout = async () => {
    await profileApiService.logout();
    router.push("/login");
  };
  const router = useRouter();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const unreadReminderCount = useSelector(selectUnreadReminderCount);
  return (
    <nav className="flex justify-between w-full items-center">
      <Breadcrumbs />
      <div className="flex gap-4 items-center">
        <SidebarTrigger className="w-9 h-9" variant={"outline"} size={"icon"} />
        <DarkModeToggle />
        <Button
          className="cursor-pointer relative"
          variant="outline"
          size="icon"
          aria-label={
            unreadReminderCount > 0
              ? `Reminders (${unreadReminderCount} new)`
              : "Reminders"
          }
          onClick={() => router.push("/reminders")}
        >
          <Bell />
          {unreadReminderCount > 0 && (
            <span className="absolute -top-1.5 -right-1.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[10px] font-semibold leading-none text-white">
              {unreadReminderCount > 9 ? "9+" : unreadReminderCount}
            </span>
          )}
        </Button>
        <Button
          className="cursor-pointer"
          variant="outline"
          size="icon"
          onClick={() => router.push("/profile")}
        >
          <UserRound />
        </Button>
        <Button
          className="cursor-pointer"
          variant="outline"
          size="icon"
          onClick={() => setIsModalOpen(true)}
        >
          <LogOut />
        </Button>
      </div>
      <AlertModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        variant="warning"
        description="Are you sure you want to log out?"
        title="Loging out"
        showCancel
        onConfirm={confirmLogout}
      />
    </nav>
  );
};

export default Navbar;
