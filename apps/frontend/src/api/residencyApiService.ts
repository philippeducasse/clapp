import { Residency } from "@/interfaces/entities/Residency";
import {
  fetchRequest,
  sendRequest,
  deleteRequest,
  sendFormDataRequest,
  patchRequest,
} from "./fetchHelper";
import { ApplicationCreate } from "@/interfaces/entities/Application";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { TagAction } from "@/interfaces/Enums";
import { EntityApiService } from "@/interfaces/api/ApiService";

const endpoint = "/api/residencies/";

const getAll = (): Promise<PaginatedResponse<Residency>> => {
  return fetchRequest<PaginatedResponse<Residency>>(endpoint);
};

const get = (id: number): Promise<Residency> => {
  return fetchRequest(`${endpoint}${id}/`);
};

const create = (residency: Residency): Promise<Residency> => {
  return sendRequest(`${endpoint}`, residency, "POST", "Residency successfully created");
};

const remove = (residencyId: number): Promise<void> => {
  return deleteRequest(`${endpoint}${residencyId}`, "Residency successfully deleted");
};

const tag = (residencyId: number, action: TagAction): Promise<Residency> => {
  return patchRequest<Residency>(
    `${endpoint}${residencyId}/tag/${action}/`,
    "Residency successfully tagged"
  );
};

const update = (residency: Residency): Promise<Residency> => {
  return sendRequest(
    `${endpoint}${residency.id}/`,
    residency,
    "PUT",
    "Residency successfully updated"
  );
};

const enrich = (id: number): Promise<Residency> => {
  return fetchRequest(`${endpoint}${id}/enrich/`);
};

const apply = (
  residencyId: number,
  application: ApplicationCreate,
  files: File[],
  fileFieldName: string
): Promise<{ message: string; applicationId: number }> => {
  return sendFormDataRequest<ApplicationCreate, { message: string; applicationId: number }>(
    `${endpoint}${residencyId}/apply/`,
    application,
    files,
    fileFieldName,
    "POST",
    "Application successfully sent"
  );
};

const generateEmail = (residencyId: number) => {
  return sendRequest<{ message: string }, { message: string }>(
    `${endpoint}${residencyId}/generate_email/`,
    { message: "" },
    "POST",
    "Email successfully generated"
  );
};

export const residencyApiService: EntityApiService<Residency> = {
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
