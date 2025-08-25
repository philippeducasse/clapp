import {
  NavigationMenu,
  // NavigationMenuItem,
  // NavigationMenuLink,
  // NavigationMenuList,
  // navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import { DarkModeToggle } from "@/components/ui/dark-mode-toggle";
import { SidebarTrigger } from "@/components/ui/sidebar";
import Breadcrumbs from "./Breadcrumbs";

const Navbar = () => {
  // const navItems = ["Home", "Festivals", "Applications", "Invoices", "Settings"];

  return (
    <NavigationMenu viewport={false} className="flex justify-between">
      <Breadcrumbs />
      <DarkModeToggle />
      <SidebarTrigger className="self-end" />
      {/* 
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
      </NavigationMenuList> */}
    </NavigationMenu>
  );
};

export default Navbar;
