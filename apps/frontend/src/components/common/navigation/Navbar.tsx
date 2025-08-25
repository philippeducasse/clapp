import { DarkModeToggle } from "@/components/ui/dark-mode-toggle";
import { SidebarTrigger } from "@/components/ui/sidebar";
import Breadcrumbs from "./Breadcrumbs";

const Navbar = () => {
  return (
    <nav className="flex justify-between w-full items-center">
      <Breadcrumbs />
      <div className="flex gap-4 items-center">
        <DarkModeToggle />
        <SidebarTrigger className="" />
      </div>
    </nav>
  );
};

export default Navbar;
