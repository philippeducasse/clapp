import { SectionCellProps, SectionCellType } from "@/interfaces/DetailsView";
import { EmailTemplate } from "@/interfaces/entities/Profile";
import { Profile } from "@/interfaces/entities/Profile";
export const getEmailTemplateInfo = (template: EmailTemplate): SectionCellProps[] => {
  if (!template) return [];

  const info: SectionCellProps[] = [{ title: "Name", value: template.name }];

  if (template.subjectTemplate) {
    info.push({ title: "Subject Template", value: template.subjectTemplate });
  }

  info.push({ title: "Content", value: template.content, type: SectionCellType.HTML });

  return info;
};

export const getDefaultEmailSubject = (profile: Profile): SectionCellProps[] => {
  return [{ title: "Default subject", value: profile.emailSubjectDefultText }];
};
