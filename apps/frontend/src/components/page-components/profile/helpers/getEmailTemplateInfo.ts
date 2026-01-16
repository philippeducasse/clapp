import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { EmailTemplate } from "@/interfaces/entities/Profile";

export const getEmailTemplateInfo = (template: EmailTemplate): SectionCellProps[] => {
  if (!template) return [];

  return [
    { title: "Name", value: template.name },
    { title: "Content", value: template.content, type: SectionCellType.HTML },
  ];
};
