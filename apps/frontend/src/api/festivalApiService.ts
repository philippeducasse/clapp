import { Festival } from "@/interfaces/entities/Festival";
import {
  fetchRequest,
  sendRequest,
  deleteRequest,
  sendFormDataRequest,
  patchRequest,
} from "./fetchHelper";
import { ApplicationCreate } from "@/interfaces/entities/Application";
import { Profile } from "@/interfaces/entities/Profile";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { TagAction } from "@/interfaces/Enums";
import { EntityApiService } from "@/interfaces/api/ApiService";

const endpoint = "/api/festivals/";

const getAll = (): Promise<PaginatedResponse<Festival>> => {
  return fetchRequest<PaginatedResponse<Festival>>(endpoint);
};

const get = (festivalId: number): Promise<Festival> => {
  return fetchRequest<Festival>(`${endpoint}${festivalId}/`);
};

const create = (festival: Festival): Promise<Festival> => {
  return sendRequest<Festival, Festival>(
    `${endpoint}`,
    festival,
    "POST",
    "Festival successfully created",
    true
  );
};

const tag = (festivalId: number, action: TagAction): Promise<Festival> => {
  return patchRequest<Festival>(
    `${endpoint}${festivalId}/tag/${action}/`,
    "Festival successfully tagged"
  );
};

const remove = (festivalId: number): Promise<void> => {
  return deleteRequest(`${endpoint}${festivalId}/`, "Festival successfully deleted", true);
};

const enrich = (festivalId: number): Promise<Festival> => {
  return fetchRequest<Festival>(`${endpoint}${festivalId}/enrich/`);
};

const update = (festival: Festival): Promise<Festival> => {
  return sendRequest<Festival, Festival>(
    `${endpoint}${festival.id}/`,
    festival,
    "PUT",
    "Festival successfully updated",
    true
  );
};

const generateEmail = (
  festivalId: number,
  data: { profile: Profile; selectedPerformanceIds?: number[] }
): Promise<{ message: string }> => {
  return sendRequest<{ profile: Profile; selectedPerformanceIds?: number[] }, { message: string }>(
    `${endpoint}${festivalId}/generate_email/`,
    data,
    "POST",
    "Email successfully generated",
    true
  );
};

const apply = (
  festivalId: number,
  application: ApplicationCreate,
  files: File[],
  fileFieldName: string
): Promise<{ message: string; applicationId: number }> => {
  return sendFormDataRequest<ApplicationCreate, { message: string; applicationId: number }>(
    `${endpoint}${festivalId}/apply/`,
    application,
    files,
    fileFieldName,
    "POST",
    "Application successfully sent"
  );
};

export const festivalApiService: EntityApiService<Festival> = {
  getAll,
  get,
  create,
  update,
  remove,
  tag,
  enrich,
  apply,
  generateEmail,
};
