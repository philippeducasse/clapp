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
  attachmentsReceived?: File[];
  answerReceived?: boolean;
  answerDate?: string;
  applicationStatus: ApplicationStatus;
  followUpDate?: string;
  responseDetails?: string;
  performanceDetails?: string;
  contractReceived?: boolean;
  contractSigned?: boolean;
  paymentReceived?: boolean;
  paymentAmount?: number;
  comments?: string;
  createdAt: string;
  updatedAt?: string;
}

export type ApplicationCreate = Partial<
  Omit<Application, "id" | "createdAt" | "updatedAt" | "festival">
> & {
  // profileId: number;
};

export enum ApplicationMethod {
  EMAIL = "EMAIL",
  FORM = "FORM",
  INVITATION_ONLY = "INVITATION_ONLY",
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
