import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";
import { Application } from "@/interfaces/entities/Application";
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

export const applicationApiService = {
  getAll,
  get,
  create,
  update,
  remove,
};
