"use client";

import { DarkModeToggle } from "@/components/ui/dark-mode-toggle";
import Breadcrumbs from "./Breadcrumbs";
import { UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";

const Navbar = () => {
  const router = useRouter();

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
          <UserRound className="" />
        </Button>
      </div>
    </nav>
  );
};

export default Navbar;
