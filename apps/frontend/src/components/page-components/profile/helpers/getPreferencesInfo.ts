import { SectionCellProps } from "@/interfaces/DetailsView";
import { Profile } from "@/interfaces/entities/Profile";

export const getPreferencesInfo = (profile: Profile): SectionCellProps[] => {
  if (!profile) return [];

  const dateFormatLabel: Record<string, string> = {
    "DD/MM/YYYY": "DD/MM/YYYY",
    "MM/DD/YYYY": "MM/DD/YYYY",
    "YYYY-MM-DD": "YYYY-MM-DD",
  };

  const tableSizeLabel: Record<string, string> = {
    compact: "Compact (10 rows)",
    medium: "Medium (25 rows)",
    large: "Large (50 rows)",
  };

  return [
    {
      title: "Date Format",
      value: profile.dateFormat ? dateFormatLabel[profile.dateFormat] : "Not set",
    },
    {
      title: "Table Size",
      value: profile.tableSize ? tableSizeLabel[profile.tableSize] : "Not set",
    },
  ];
};