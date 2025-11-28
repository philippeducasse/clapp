"use client";

import { DarkModeToggle } from "@/components/ui/dark-mode-toggle";
import Breadcrumbs from "./Breadcrumbs";
import { UserRound, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { AlertModal } from "../modals/AlertModal";
import { useState } from "react";
import { profileApiService } from "@/api/profileApiService";
const Navbar = () => {
  const confirmLogout = async () => {
    await profileApiService.logout();
    router.push("/");
  };
  const router = useRouter();
  const [isModalOpen, setIsModalOpen] = useState(false);
  return (
    <nav className="flex justify-between w-full items-center">
      <Breadcrumbs />
      <div className="flex gap-4 items-center">
        <DarkModeToggle />
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
