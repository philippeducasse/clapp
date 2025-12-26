import { ControlledFormElement } from "@/interfaces/forms/ControlledFormElement";
import { ControlledFormElementType } from "@/interfaces/forms/ControlledFormElementType";
import { LANGUAGES } from "@/constants/languages";

export const getProfileFormFields = (): ControlledFormElement[] => {
  const fields: ControlledFormElement[] = [
    {
      label: "Profile ID",
      fieldName: "id",
      type: ControlledFormElementType.NUMBER,
      hidden: true,
    },
    // Basic Information
    {
      label: "Email",
      fieldName: "email",
      type: ControlledFormElementType.EMAIL,
      required: true,
    },
    {
      label: "First Name",
      fieldName: "firstName",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Last Name",
      fieldName: "lastName",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Company Name",
      fieldName: "companyName",
      type: ControlledFormElementType.TEXT,
      helpText: "Company or organization name",
    },
    {
      label: "Location",
      fieldName: "location",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Nationality",
      fieldName: "nationality",
      type: ControlledFormElementType.TEXT,
    },
    {
      label: "Spoken Languages",
      fieldName: "spokenLanguages",
      type: ControlledFormElementType.MULTI_SELECT,
      options: LANGUAGES.map((lang) => ({ value: lang.code, label: lang.name })),
      defaultValue: [],
      helpText: "Select all languages you can communicate in",
    },
    {
      label: "Personal Website",
      fieldName: "personalWebsite",
      type: ControlledFormElementType.URL,
    },
    {
      label: "Instagram Profile",
      fieldName: "instagramProfile",
      type: ControlledFormElementType.URL,
      helpText: "Full URL to Instagram profile",
    },
    {
      label: "Facebook Profile",
      fieldName: "facebookProfile",
      type: ControlledFormElementType.URL,
      helpText: "Full URL to Facebook profile",
    },
    {
      label: "YouTube Profile",
      fieldName: "youtubeProfile",
      type: ControlledFormElementType.URL,
      helpText: "Full URL to YouTube channel",
    },
    {
      label: "TikTok Profile",
      fieldName: "tiktokProfile",
      type: ControlledFormElementType.URL,
      helpText: "Full URL to TikTok profile",
    },
  ];

  return fields;
};
