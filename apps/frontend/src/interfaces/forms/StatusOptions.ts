import { SelectOptions } from "./ControlledFormElement";
import { ApplicationStatus } from "../entities/Application";

export const ApplicationStatusOptions: SelectOptions[] = [
  { value: ApplicationStatus.DRAFT, label: "Draft" },
  { value: ApplicationStatus.APPLIED, label: "Applied" },
  { value: ApplicationStatus.AUTO_REPLY_RECEIVED, label: "Auto-reply received" },
  { value: ApplicationStatus.IN_DISCUSSION, label: "In discussion" },
  { value: ApplicationStatus.REJECTED, label: "Rejected" },
  { value: ApplicationStatus.IGNORED, label: "Ignored" },
  { value: ApplicationStatus.ACCEPTED, label: "Accepted" },
  { value: ApplicationStatus.POSTPONED, label: "Postponed" },
  { value: ApplicationStatus.CANCELLED, label: "Cancelled" },
  { value: ApplicationStatus.OTHER, label: "Other" },
];
