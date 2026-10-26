import { UploadStats } from "@/components/page-components/upload/UploadForm";
import { fetchRequest, sendFormDataRequest, sendRequest } from "./fetchHelper";
import { OrganisationType } from "@/interfaces/Enums";
import { ORGANISATION_ROUTES } from "@/helpers/organisationRoutes";

const endpoint = "/api/organisations";

export interface OrganisationSearchResponse {
  id: number;
  name: string;
  country: string;
  town: string;
  type: string;
}

export interface ConvertOrganisationResponse {
  id: number;
  organisationType: OrganisationType;
}

interface TaskResponse {
  taskId: string;
}

interface TaskStatus {
  status: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE";
  stats: UploadStats | null;
}

const search = async (
  searchQuery: string,
  type?: string,
): Promise<OrganisationSearchResponse[]> => {
  if (!searchQuery || searchQuery.length < 2) {
    return [];
  }
  const typeParam = type ? `&type=${type.toLowerCase()}` : "";
  return await fetchRequest(`${endpoint}/search?q=${searchQuery}${typeParam}`);
};

const upload = async (excelFile: File[]): Promise<string> => {
  const response = await sendFormDataRequest<TaskResponse>(
    `${endpoint}/upload`,
    undefined,
    excelFile,
    "excel",
    "POST",
  );
  return response.taskId;
};

const pollTask = async (taskId: string): Promise<UploadStats> => {
  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const { status, stats } = await fetchRequest<TaskStatus>(
          `${endpoint}/upload-status/${taskId}`,
        );

        if (status === "SUCCESS") {
          clearInterval(interval);
          resolve(stats!);
        } else if (status === "FAILURE") {
          clearInterval(interval);
          reject(new Error("Upload task failed"));
        }
      } catch (error) {
        clearInterval(interval);
        reject(error);
      }
    }, 2000);

    setTimeout(
      () => {
        clearInterval(interval);
        reject(new Error("Upload task timeout"));
      },
      5 * 60 * 1000, // 5 minutes
    );
  });
};

/**
 * Change an organisation's type (e.g. festival -> venue). The organisation gets a
 * new id; contacts, applications and reminders move with it.
 */
const convert = (
  type: OrganisationType,
  id: number,
  targetType: OrganisationType,
): Promise<ConvertOrganisationResponse> =>
  sendRequest<{ targetType: OrganisationType }, ConvertOrganisationResponse>(
    `/api${ORGANISATION_ROUTES[type]}/${id}/convert`,
    { targetType },
    "POST",
    "Organisation type changed",
  );

export const organisationApiService = {
  search,
  convert,
  upload,
  pollTask,
};
