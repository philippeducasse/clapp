import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { Profile } from "@/interfaces/entities/Profile";
import { capitalize } from "lodash";

export const getProfileContactInfo = (profile: Profile): SectionCellProps[] => {
  if (!profile) return [];

  return [
    { title: "Website", value: profile.personalWebsite, type: SectionCellType.Link },
    { title: "Instagram", value: profile.instagramProfile, type: SectionCellType.Link },
    { title: "Facebook", value: profile.facebookProfile, type: SectionCellType.Link },
    { title: "Youtube", value: profile.youtubeProfile, type: SectionCellType.Link },
    { title: "Tiktok", value: profile.tiktokProfile, type: SectionCellType.Link },
  ];
};
