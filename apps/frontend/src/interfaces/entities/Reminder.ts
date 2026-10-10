import { OrganisationType } from "../Enums";

export interface Reminder {
  id: number;
  objectId: number;
  organisationType: OrganisationType;
  organisationName?: string;
  message: string;
  remindAt: string;
  isSent?: boolean;
  /** Set when the reminder fired (in-app delivery), independent of the email */
  deliveredAt?: string | null;
  /** Set once the user has seen the delivered reminder */
  readAt?: string | null;
  createdAt?: string;
}

export interface ReminderCreate {
  organisationType: OrganisationType;
  objectId: number;
  message: string;
  remindAt: string;
}
