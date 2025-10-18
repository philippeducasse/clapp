import { SelectOptions } from "./ControlledFormElement";
import { ApplicationStatus } from "../entities/Application";

export const ApplicationStatusOptions: SelectOptions[] = [
  { value: ApplicationStatus.ACCEPTED, label: "Accepted" },
  { value: ApplicationStatus.APPLIED, label: "Applied" },
  { value: ApplicationStatus.CANCELLED, label: "Cancelled" },
  { value: ApplicationStatus.IGNORED, label: "Ignored" },
  { value: ApplicationStatus.IN_DISCUSSION, label: "In discussion" },
  { value: ApplicationStatus.NOT_APPLIED, label: "Not Applied" },
  { value: ApplicationStatus.OTHER, label: "Other" },
  { value: ApplicationStatus.POSTPONED, label: "Postponed" },
  { value: ApplicationStatus.REJECTED, label: "Rejected" },
  { value: ApplicationStatus.DRAFT, label: "Draft" },
];
