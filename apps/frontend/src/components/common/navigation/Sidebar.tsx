import {
  Home,
  Flag,
  ClipboardEdit,
  Settings,
  Upload,
  CircleQuestionMark,
  University,
  Theater,
  Bug,
} from "lucide-react";

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
    title: "Report a bug",
    url: "/bug",
    icon: Bug,
  },
  {
    title: "Help",
    url: "/help",
    icon: CircleQuestionMark,
  },
  {
    title: "Upload your data",
    url: "/upload",
    icon: Upload,
  },
  {
    title: "Settings",
    url: "/settings",
    icon: Settings,
  },
];

const Sidebar = () => {
  return (
    <ShadcnSidebar>
      <SidebarContent>
        <SidebarGroup className="h-full">
          <SidebarGroupLabel className="text-emerald-600 mb-8 mt-5 text-lg dark:text-emerald-400">
            Application Agent
          </SidebarGroupLabel>
          <SidebarGroupContent className="h-full">
            <SidebarMenu className="flex h-full">
              {items.map((item, index) => (
                <SidebarMenuItem key={item.title} className={index == 5 ? `mt-auto` : ""}>
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
