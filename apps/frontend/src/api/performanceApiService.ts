import { Performance } from "@/interfaces/entities/Performance";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";

const endpoint = "/api/performances/";

const getAll = (userId: number): Promise<Performance[]> => {
  return fetchRequest<Performance[]>(`${endpoint}${userId}/`);
};

const get = (performanceId: number): Promise<Performance> => {
  return fetchRequest<Performance>(`${endpoint}${performanceId}/`);
};

const create = (performance: Performance): Promise<Performance> => {
  return sendRequest<Performance, Performance>(
    `${endpoint}`,
    performance,
    "POST",
    "Performance successfully created",
    true
  );
};

const remove = (performanceId: number) => {
  return deleteRequest(`${endpoint}${performanceId}`, "Performance successfully deleted", true);
};

const update = (performance: Performance): Promise<Performance> => {
  return sendRequest<Performance, Performance>(
    `${endpoint}${performance.id}/`,
    performance,
    "PUT",
    "Performance successfully updated",
    true
  );
};

export const performanceApiService = {
  getAll,
  get,
  create,
  update,
  remove,
};
