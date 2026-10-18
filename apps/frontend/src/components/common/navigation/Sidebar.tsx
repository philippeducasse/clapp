"use client";

import { useSelector } from "react-redux";
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
import Image from "next/image";
import Link from "next/link";
import { selectProfile } from "@/redux/slices/authSlice";
import { getSidebarItems } from "./sidebarItems";

const Sidebar = () => {
  const profile = useSelector(selectProfile);
  const items = getSidebarItems(profile?.isSuperuser);

  return (
    <ShadcnSidebar>
      <SidebarContent>
        <SidebarGroup className="h-full">
          <SidebarGroupLabel className="text-primary mb-8 mt-5 gap-1">
            <h1 className="font-clapp text-4xl">Clapp</h1>
            <Image
              src={"/logo.png"}
              width="60"
              height="60"
              alt="Clapping hands"
            />
          </SidebarGroupLabel>
          <SidebarGroupContent className="h-full my-6">
            <SidebarMenu className="flex h-full">
              {items.map((item) => (
                <SidebarMenuItem
                  key={item.title}
                  className={item.bottom ? "mt-auto" : ""}
                >
                  <SidebarMenuButton asChild size={"lg"}>
                    <Link href={item.url}>
                      <item.icon className="text-primary h-6! w-6!" />
                      <span className="text-lg ml-4">{item.title}</span>
                    </Link>
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
