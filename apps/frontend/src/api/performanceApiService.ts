import { Performance } from "@/interfaces/entities/Performance";
import { fetchRequest, sendRequest, deleteRequest, sendFormDataRequest } from "./fetchHelper";

const endpoint = "/api/performances/";

const getAll = (userId: number): Promise<Performance[]> => {
  return fetchRequest<Performance[]>(`${endpoint}${userId}/`);
};

const get = (performanceId: number): Promise<Performance> => {
  return fetchRequest<Performance>(`${endpoint}${performanceId}/`);
};

const create = (performance: Performance): Promise<Performance> => {
  const { dossierFiles, ...performanceData } = performance as Performance & { dossierFiles?: File[] };

  if (dossierFiles && dossierFiles.length > 0) {
    return sendFormDataRequest<Performance, Performance>(
      `${endpoint}`,
      performanceData,
      dossierFiles,
      "dossier_files",
      "POST",
      "Performance successfully created"
    );
  }

  return sendRequest<Performance, Performance>(
    `${endpoint}`,
    performanceData,
    "POST",
    "Performance successfully created",
    true
  );
};

const remove = (performanceId: number) => {
  return deleteRequest(`${endpoint}${performanceId}`, "Performance successfully deleted", true);
};

const update = (performance: Performance): Promise<Performance> => {
  const { dossierFiles, ...performanceData } = performance as Performance & {
    dossierFiles?: Array<File | { id: number; file: string; uploadedAt: Date | string }>
  };

  if (dossierFiles && dossierFiles.length > 0) {
    const existingDossiers = dossierFiles.filter((item): item is { id: number; file: string; uploadedAt: Date | string } =>
      !(item instanceof File)
    );
    const newFiles = dossierFiles.filter((item): item is File => item instanceof File);

    const dataWithDossierIds = {
      ...performanceData,
      dossierIds: existingDossiers.map(d => d.id),
    };

    if (newFiles.length > 0) {
      return sendFormDataRequest<Performance, Performance>(
        `${endpoint}${performance.id}/`,
        dataWithDossierIds,
        newFiles,
        "dossier_files",
        "PUT",
        "Performance successfully updated"
      );
    }

    // No new files, but send dossier_ids to keep existing ones
    return sendRequest<Performance, Performance>(
      `${endpoint}${performance.id}/`,
      dataWithDossierIds,
      "PUT",
      "Performance successfully updated",
      true
    );
  }

  // No dossiers at all, send empty dossier_ids to delete all
  return sendRequest<Performance, Performance>(
    `${endpoint}${performance.id}/`,
    { ...performanceData, dossierIds: [] },
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
