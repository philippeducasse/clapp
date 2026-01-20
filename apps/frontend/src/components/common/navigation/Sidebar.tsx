import { Home, Flag, ClipboardEdit, Settings, University, Theater } from "lucide-react";

import {
  Sidebar as ShadcnSidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

// Menu items.
const items = [
  {
    title: "Home",
    url: "/",
    icon: Home,
  },
  {
    title: "Festivals",
    url: "/festivals",
    icon: Flag,
  },
  {
    title: "Venues",
    url: "/venues",
    icon: Theater,
  },
  {
    title: "Residencies",
    url: "/residencies",
    icon: University,
  },
  {
    title: "Applications",
    url: "/applications",
    icon: ClipboardEdit,
  },
  {
    title: "Settings",
    url: "#",
    icon: Settings,
  },
];

const Sidebar = () => {
  return (
    <ShadcnSidebar>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="text-emerald-600 mb-8 mt-5 text-lg dark:text-emerald-400">
            Application Agent
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <a href={item.url}>
                      <item.icon className="text-emerald-600 h-6! w-6! dark:text-emerald-400" />
                      <span className="text-lg ml-4">{item.title}</span>
                    </a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </ShadcnSidebar>
  );
};

export default Sidebar;
