import { Performance } from "./Performance";
import { EmailHost } from "../Enums";

export interface EmailTemplate {
  [key: string]: unknown;
  id: number;
  name: string;
  content: string;
}

export interface Profile {
  [key: string]: unknown;
  id: number;
  email: string;
  firstName?: string;
  lastName?: string;
  companyName?: string;
  personalWebsite?: string;
  location?: string;
  nationality?: string;
  spokenLanguages?: string[];
  instagramProfile?: string;
  facebookProfile?: string;
  tiktokProfile?: string;
  youtubeProfile?: string;
  performances: Performance[];
  emailTemplates?: EmailTemplate[];
  emailHost?: EmailHost;
  otherEmailHost?: string;
  emailPort?: number;
  emailUseTls?: boolean;
  emailHostUser?: string;
  emailHostPassword?: string;
}
