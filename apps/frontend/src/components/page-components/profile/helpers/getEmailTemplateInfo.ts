import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { EmailTemplate } from "@/interfaces/entities/Profile";
import { Profile } from "@/interfaces/entities/Profile";
export const getEmailTemplateInfo = (template: EmailTemplate): SectionCellProps[] => {
  console.log(template);
  return [
    { title: "Name", value: template.name },
    { title: "Subject", value: template.subject },
    { title: "Content", value: template.content, type: SectionCellType.HTML },
  ];
};

export const getDefaultEmailSubject = (profile: Profile): SectionCellProps[] => {
  return [{ title: "Default subject", value: profile.defaultEmailSubject }];
};
