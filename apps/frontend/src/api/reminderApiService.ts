import { Reminder, ReminderCreate } from "@/interfaces/entities/Reminder";
import { OrganisationType } from "@/interfaces/Enums";
import { sendRequest, deleteRequest, fetchRequest } from "./fetchHelper";

export const reminderEndpoint = "/api/profiles/me/reminders";

const setReminder = (reminder: ReminderCreate): Promise<Reminder> => {
  return sendRequest<ReminderCreate, Reminder>(
    reminderEndpoint,
    reminder,
    "POST",
    "Reminder successfully set",
    true,
  );
};

const deleteReminder = (reminderId: number): Promise<void> => {
  return deleteRequest(`${reminderEndpoint}/${reminderId}`, "Reminder successfully deleted");
};

const getReminders = (): Promise<Reminder[]> => {
  return fetchRequest<Reminder[]>(reminderEndpoint);
};

const getRemindersForEntity = (
  organisationType: OrganisationType,
  objectId: number,
): Promise<Reminder[]> => {
  const params = new URLSearchParams({
    organisation_type: organisationType,
    object_id: objectId.toString(),
  });
  return fetchRequest<Reminder[]>(`${reminderEndpoint}?${params.toString()}`);
};

export const reminderApiService = {
  setReminder,
  deleteReminder,
  getReminders,
  getRemindersForEntity,
};
