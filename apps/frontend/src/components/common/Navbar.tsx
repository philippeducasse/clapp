import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { DarkModeToggle } from "../ui/dark-mode-toggle";
import { SidebarTrigger } from "../ui/sidebar";
import Breadcrumbs from "./Breadcrumbs";

const Navbar = () => {
  const navItems = ["Home", "Festivals", "Applications", "Invoices", "Settings"];

  return (
    <NavigationMenu viewport={false} className="mx-auto">
      <SidebarTrigger />
      <Breadcrumbs />
      <NavigationMenuList>
        {navItems.map((item) => (
          <NavigationMenuItem key={item}>
            <NavigationMenuLink
              href={item === "Home" ? "/" : `/${item.toLowerCase()}`}
              className={navigationMenuTriggerStyle()}
            >
              {item}
            </NavigationMenuLink>
          </NavigationMenuItem>
        ))}
        <DarkModeToggle />
      </NavigationMenuList>
    </NavigationMenu>
  );
};

export default Navbar;
