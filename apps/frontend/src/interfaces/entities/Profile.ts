import { Performance } from "./Performance";
import { EmailHost } from "../Enums";

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
  emailHost?: EmailHost;
  otherEmailHost?: string;
  emailPort?: number;
  emailUseTls?: boolean;
  emailHostUser?: string;
  emailHostPassword?: string;
}
