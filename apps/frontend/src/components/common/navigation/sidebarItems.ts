import {
  Home,
  Flag,
  ClipboardEdit,
  Upload,
  CircleQuestionMark,
  University,
  Theater,
  Bug,
  UserRound,
  Mail,
  Compass,
  LucideIcon,
} from "lucide-react";

export interface SidebarItem {
  title: string;
  url: string;
  icon: LucideIcon;
  /** Only shown to superusers. */
  superuserOnly?: boolean;
  /** Pushes this item, and the ones after it, to the bottom of the sidebar. */
  bottom?: boolean;
}

export const SIDEBAR_ITEMS: SidebarItem[] = [
  { title: "Home", url: "/dashboard", icon: Home },
  { title: "Festivals", url: "/festivals", icon: Flag },
  { title: "Venues", url: "/venues", icon: Theater },
  { title: "Residencies", url: "/residencies", icon: University },
  { title: "Applications", url: "/applications", icon: ClipboardEdit },
  { title: "Inbound emails", url: "/inbound-emails", icon: Mail },
  { title: "Discover", url: "/discover", icon: Compass, superuserOnly: true },
  { title: "Report a bug", url: "/report-bug", icon: Bug, bottom: true },
  { title: "Help", url: "/help", icon: CircleQuestionMark },
  { title: "Upload your data", url: "/upload", icon: Upload },
  { title: "Profile", url: "/profile", icon: UserRound },
];

export const getSidebarItems = (isSuperuser: boolean | undefined): SidebarItem[] =>
  SIDEBAR_ITEMS.filter((item) => !item.superuserOnly || isSuperuser === true);
