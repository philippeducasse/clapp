import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { TagAction } from "@/interfaces/Enums";
import { ApplicationCreate } from "@/interfaces/entities/Application";
import { Profile } from "../entities/Profile";
import { Reminder, ReminderCreate } from "../entities/Reminder";

export interface EntityApiService<T> {
  getAll: () => Promise<PaginatedResponse<T>>;
  get: (id: number) => Promise<T>;
  create: (entity: T) => Promise<T>;
  update: (entity: T) => Promise<T>;
  remove: (id: number) => Promise<void>;
  tag: (entityId: number, action: TagAction) => Promise<T>;
  enrich: (id: number) => Promise<T>;
  apply: (
    entityId: number,
    application: ApplicationCreate,
    files: File[],
    fileFieldName: string,
  ) => Promise<{ message: string; applicationId: number } | ApplicationCreate>;
  generateEmail: (
    entityId: number,
    data: { profile: Profile; selectedPerformanceIds?: number[]; language: string },
  ) => Promise<{ message: string }>;
  setReminder: (reminder: ReminderCreate) => Promise<Reminder>;
  deleteReminder: (reminderId: number) => Promise<void>;
}

export interface Credentials {
  email: string;
  password: string;
}

export const reminderEndpoint = "/api/organisations/reminders/";
