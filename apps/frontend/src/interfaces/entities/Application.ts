import { Festival } from "./Festival";
import { Profile } from "./Profile";
import { Residency } from "./Residency";
import { Venue } from "./Venue";
import { Performance } from "./Performance";

export interface Application {
  id?: number;
  organisation: Festival | Venue | Residency;
  organisationType: "Festival" | "Residency" | "Venue";
  profile: number | Profile;
  applicationDate: string;
  applicationMethod: ApplicationMethod;
  performances?: Performance[];
  emailSubject?: string;
  applicationSeason?: ApplicationSeason;
  season?: string | null;
  message?: string;
  attachmentsSent?: File[];
  status: ApplicationStatus;
  comments?: string;
  createdAt: string;
  updatedAt?: string;
  emailRecipients?: string[];
  applicationYear?: number;
}

export interface ApplicationSeason {
  id: number;
  name: string;
  createdAt?: string;
}

// Filter value for "applications without a season". Must match NO_SEASON in the backend's applications/views.py.
export const NO_SEASON_FILTER = "__none__";

export type ApplicationCreate = Partial<
  Omit<Application, "id" | "createdAt" | "updatedAt" | "festival">
> & {
  profileId: number;
  objectType: string;
  objectId: number;
};

export enum ApplicationMethod {
  EMAIL = "EMAIL",
  FORM = "FORM",
  INVITATION = "INVITATION",
  OTHER = "OTHER",
  UNKNOWN = "UNKNOWN",
}

export enum ApplicationStatus {
  DRAFT = "DRAFT",
  APPLIED = "APPLIED",
  AUTO_REPLY_RECEIVED = "AUTO_REPLY_RECEIVED",
  IN_DISCUSSION = "IN_DISCUSSION",
  REJECTED = "REJECTED",
  IGNORED = "IGNORED",
  ACCEPTED = "ACCEPTED",
  POSTPONED = "POSTPONED",
  CANCELLED = "CANCELLED",
  OTHER = "OTHER",
}
