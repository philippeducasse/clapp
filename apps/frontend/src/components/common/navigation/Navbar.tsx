import { DarkModeToggle } from "@/components/ui/dark-mode-toggle";
import Breadcrumbs from "./Breadcrumbs";

const Navbar = () => {
  return (
    <nav className="flex justify-between w-full items-center">
      <Breadcrumbs />
      <div className="flex gap-4 items-center">
        <DarkModeToggle />
      </div>
    </nav>
  );
};

export default Navbar;
