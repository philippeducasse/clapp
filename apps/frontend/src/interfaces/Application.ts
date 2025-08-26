export interface Application {
  id?: number;
  festival: number;
  applicationDate: string | null;
  applicationMethod: ApplicationMethod | null;
  emailSubject?: string;
  message?: string;
  attachmentsSent?: File[] | null;
  attachmentsReceived?: File[] | null;
  answerReceived?: boolean;
  answerDate?: string | null;
  applicationStatus: ApplicationStatus;
  followUpDate?: string | null;
  responseDetails?: string | null;
  performanceDetails?: string | null;
  contractReceived?: boolean | null;
  contractSigned?: boolean | null;
  paymentReceived?: boolean | null;
  paymentAmount?: number | null;
  comments?: string | null;
  createdAt: string;
  updatedAt?: string;
}

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
}
