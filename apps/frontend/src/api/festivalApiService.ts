import { Festival } from "@/interfaces/entities/Festival";
import {
  fetchRequest,
  sendRequest,
  deleteRequest,
  sendFormDataRequest,
  patchRequest,
} from "./fetchHelper";
import { Application, ApplicationCreate } from "@/interfaces/entities/Application";
import { Profile } from "@/interfaces/entities/Profile";
import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { TagAction } from "@/interfaces/Enums";
import { EntityApiService } from "@/interfaces/api/ApiService";

const endpoint = "http://localhost:8000/api/festivals/";

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
    "Festival successfully created"
  );
};

const tag = (festivalId: number, action: TagAction): Promise<Festival> => {
  return patchRequest<Festival>(
    `${endpoint}${festivalId}/tag/${action}/`,
    "Festival successfully tagged"
  );
};

const remove = (festivalId: number): Promise<void> => {
  return deleteRequest(`${endpoint}${festivalId}`, "Festival successfully deleted");
};

const enrich = (festivalId: number): Promise<Festival> => {
  return fetchRequest<Festival>(`${endpoint}${festivalId}/enrich/`);
};

const update = (festival: Festival): Promise<Festival> => {
  return sendRequest<Festival, Festival>(
    `${endpoint}${festival.id}/`,
    festival,
    "PUT",
    "Festival successfully updated"
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
    "Email successfully generated"
  );
};

const apply = (
  festivalId: number,
  application: Application,
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
