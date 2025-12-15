import { fetchRequest, sendRequest, deleteRequest, patchRequest } from "./fetchHelper";
import { Application, ApplicationStatus } from "@/interfaces/entities/Application";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";

const endpoint = "/api/applications/";

const getAll = (): Promise<PaginatedResponse<Application>> => {
  return fetchRequest<PaginatedResponse<Application>>(endpoint);
};

const get = (applicationId: number): Promise<Application> => {
  return fetchRequest<Application>(`${endpoint}${applicationId}/`);
};

const create = (application: Application): Promise<Application> => {
  return sendRequest<Application, Application>(
    `${endpoint}`,
    application,
    "POST",
    "Application successfully created"
  );
};

const remove = (applicationId: number) => {
  return deleteRequest(`${endpoint}${applicationId}`, "Application successfully deleted");
};

const update = (application: Application): Promise<Application> => {
  return sendRequest<Application, Application>(
    `${endpoint}${application.id}/`,
    application,
    "PUT",
    "Application successfully updated"
  );
};

const changeStatus = (entityId: number, action: ApplicationStatus): Promise<Application> => {
  return patchRequest<Application>(
    `${endpoint}${entityId}/status/${action}/`,
    "Festival status successfully updated"
  );
};

export const applicationApiService = {
  getAll,
  get,
  create,
  update,
  remove,
  changeStatus,
};
