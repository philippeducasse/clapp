import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { TagAction } from "@/interfaces/Enums";
import { Application } from "@/interfaces/entities/Application";
import { Profile } from "../entities/Profile";

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
    application: Application,
    files: File[],
    fileFieldName: string
  ) => Promise<{ message: string; applicationId: number } | Application>;
  generateEmail: (
    entityId: number,
    data: { profile: Profile; selectedPerformanceIds?: number[] }
  ) => Promise<{ message: string }>;
}
