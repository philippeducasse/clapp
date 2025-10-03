import { Performance } from "@/interfaces/entities/Performance";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";

const endpoint = "http://localhost:8000/api/performances/";

const getPerformances = (userId: number): Promise<Performance[]> => {
  return fetchRequest<Performance[]>(`${endpoint}${userId}/`);
};

const getPerformance = (performanceId: number): Promise<Performance> => {
  return fetchRequest<Performance>(`${endpoint}${performanceId}/`);
};

const createPerformance = (performance: Performance): Promise<Performance> => {
  return sendRequest<Performance, Performance>(
    `${endpoint}`,
    performance,
    "POST",
    "Performance successfully created"
  );
};

const deletePerformance = (performanceId: number) => {
  return deleteRequest(
    `${endpoint}${performanceId}`,
    "Performance successfully deleted"
  );
};

const updatePerformance = (performance: Performance): Promise<Performance> => {
  return sendRequest<Performance, Performance>(
    `${endpoint}${performance.id}/`,
    performance,
    "PUT",
    "Performance successfully updated"
  );
};

export const performanceApiService = {
  getPerformances,
  getPerformance,
  createPerformance,
  updatePerformance,
  deletePerformance,
};
