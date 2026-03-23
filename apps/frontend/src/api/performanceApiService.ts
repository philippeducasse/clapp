import { Performance } from "@/interfaces/entities/Performance";
import { fetchRequest, sendRequest, deleteRequest, sendFormDataRequest } from "./fetchHelper";

const endpoint = "/api/performances";

const getAll = (userId: number): Promise<Performance[]> => {
  return fetchRequest<Performance[]>(`${endpoint}/${userId}`);
};

const get = (performanceId: number): Promise<Performance> => {
  return fetchRequest<Performance>(`${endpoint}/${performanceId}`);
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
    "Performance successfully created"
  );
};

const remove = (performanceId: number) => {
  return deleteRequest(`${endpoint}/${performanceId}`, "Performance successfully deleted");
};

const update = (performance: Performance): Promise<Performance> => {
  const { dossierFiles, dossierIds, ...performanceData } = performance as Performance & {
    dossierFiles?: File[];
    dossierIds?: number[];
  };

  if (dossierFiles && dossierFiles.length > 0) {
    // When uploading files, use FormData but exclude dossierIds (arrays don't serialize well in FormData)
    // Backend will not delete dossiers if dossier_ids is not provided
    return sendFormDataRequest<Performance, Performance>(
      `${endpoint}/${performance.id}`,
      performanceData,
      dossierFiles,
      "dossier_files",
      "PUT",
      "Performance successfully updated"
    );
  }

  // When not uploading files, use JSON request to include dossierIds for proper array handling
  return sendRequest<Performance, Performance>(
    `${endpoint}/${performance.id}`,
    { ...performanceData, dossierIds },
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
