import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { Profile } from "@/interfaces/entities/Profile";

export const getEmailSettings = (profile: Profile): SectionCellProps[] => {
  if (!profile) return [];

  return [
    { title: "Application Email", value: profile.emailHostUser },
    {
      title: "Application Email Password",
      value: profile.emailHostPassword,
      type: SectionCellType.Password,
    },
    {
      title: "Email Host",
      value: profile.emailHost === "OTHER" ? profile.otherEmailHost : profile.emailHost,
    },
    { title: "Email Port", value: profile.emailPort },
    { title: "Email uses TLS?", value: profile.emailUseTls, type: SectionCellType.Bool },
  ];
};
