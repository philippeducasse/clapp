import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuIndicator,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  NavigationMenuViewport,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import Link from "next/link";
import { DarkModeToggle } from "../ui/dark-mode-toggle";

const Navbar = () => {
  const navItems = ["Home", "Festivals", "Applications", "Invoices", "Settings"];

  return (
    <NavigationMenu viewport={false} className="mx-auto">
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
