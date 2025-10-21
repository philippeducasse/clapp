import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { MarkAction } from "@/interfaces/Enums";

export interface EntityApiService<T> {
  getAll: () => Promise<PaginatedResponse<T>>;
  get: (id: number) => Promise<T>;
  create: (entity: T) => Promise<T>;
  update: (entity: T) => Promise<T>;
  delete: (id: number) => Promise<void>;
  mark: (entityId: number, action: MarkAction) => Promise<T>;
  enrich: (id: number) => Promise<T>;
}
