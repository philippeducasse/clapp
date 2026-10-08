import { ApplicationStatus } from "./Application";

export enum InboundEmailState {
  PENDING_REVIEW = "PENDING_REVIEW",
  UNMATCHED = "UNMATCHED",
  APPROVED = "APPROVED",
  DISMISSED = "DISMISSED",
}

export enum MatchMethod {
  HEADER = "HEADER",
  SENDER = "SENDER",
  DOMAIN = "DOMAIN",
  NAME = "NAME",
  FORM = "FORM",
  NONE = "NONE",
}

export interface InboundEmail {
  id: number;
  application: number | null;
  organisationName: string | null;
  organisationType: "festival" | "venue" | "residency" | null;
  organisationId: number | null;
  applicationStatus: ApplicationStatus | null;
  matchMethod: MatchMethod;
  isAutoReply: boolean;
  messageId: string;
  fromAddress: string;
  subject: string;
  body: string;
  receivedAt: string | null;
  suggestedStatus: ApplicationStatus | "";
  summary: string;
  state: InboundEmailState;
  createdAt: string;
}
