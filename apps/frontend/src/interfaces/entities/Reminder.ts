import { OrganisationType } from "../Enums";

export interface Reminder {
  id: number;
  objectId: number;
  organisationType: OrganisationType;
  organisationName?: string;
  message: string;
  remindAt: string;
  isSent?: boolean;
  createdAt?: string;
}

export interface ReminderCreate {
  organisationType: OrganisationType;
  objectId: number;
  message: string;
  remindAt: string;
}
