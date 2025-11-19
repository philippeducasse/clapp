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
  message?: string;
  attachmentsSent?: File[];
  applicationStatus: ApplicationStatus;
  comments?: string;
  createdAt: string;
  updatedAt?: string;
  emailRecipients?: string[];
}

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
  NOT_APPLIED = "NOT_APPLIED",
  APPLIED = "APPLIED",
  IN_DISCUSSION = "IN_DISCUSSION",
  REJECTED = "REJECTED",
  IGNORED = "IGNORED",
  ACCEPTED = "ACCEPTED",
  POSTPONED = "POSTPONED",
  CANCELLED = "CANCELLED",
  OTHER = "OTHER",
  DRAFT = "DRAFT",
}
