import { ApplicationStatus } from "./Application";

export enum InboundEmailState {
  PENDING_REVIEW = "PENDING_REVIEW",
  APPROVED = "APPROVED",
  DISMISSED = "DISMISSED",
}

export interface InboundEmail {
  id: number;
  application: number;
  organisationName: string | null;
  applicationStatus: ApplicationStatus;
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
