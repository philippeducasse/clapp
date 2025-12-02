import { SectionCellProps } from "@/interfaces/DetailsView";
import { Profile } from "@/interfaces/entities/Profile";

export const getBasicProfileInfo = (profile: Profile): SectionCellProps[] => {
  if (!profile) return [];

  return [
    { title: "Email", value: profile.email },
    { title: "First name", value: profile.firstName },
    { title: "Last name", value: profile.lastName },
    { title: "Company name", value: profile.companyName },
    { title: "location", value: profile.location },
    { title: "Nationality", value: profile.nationality },
  ];
};
