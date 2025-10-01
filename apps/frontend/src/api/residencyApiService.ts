import { Residency } from "@/interfaces/entities/Residency";
import { fetchRequest, sendRequest, deleteRequest } from "./fetchHelper";

const endpoint = "/api/residencies/";

const getResidencies = async (): Promise<Residency[]> => {
  return await fetchRequest(endpoint);
};

const getResidency = async (id: number): Promise<Residency> => {
  return await fetchRequest(`${endpoint}${id}/`);
};

const createResidency = async (
  residency: Partial<Residency>
): Promise<Residency> => {
  return await sendRequest(`${endpoint}`, residency);
};

const deleteResidency = (residencyId: number) => {
  return deleteRequest(
    `${endpoint}${residencyId}`,
    "Residency successfully deleted"
  );
};

const updateResidency = async (
  id: number,
  residency: Partial<Residency>
): Promise<Residency> => {
  return await sendRequest(`${endpoint}/${id}`, residency);
};

const enerichResidency = async (residency: Residency): Promise<Residency[]> => {
  return fetchRequest(`${endpoint}/${residency.id}/enrich/`, {
    method: "POST",
    body: JSON.stringify(residency),
  });
};

const generateEmail = (residencyId: number): Promise<{ message: string }> => {
  return sendRequest<{ message: string }>(
    `${endpoint}${residencyId}/generate_email/`,
    { message: "" },
    "POST",
    "Email successfully generated"
  );
};

export const residencyApiService = {
  getResidencies,
  getResidency,
  createResidency,
  updateResidency,
  enerichResidency,
  generateEmail,
  deleteResidency,
};
