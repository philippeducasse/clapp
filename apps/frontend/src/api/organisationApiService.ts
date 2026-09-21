import { UploadStats } from "@/components/page-components/upload/UploadForm";
import { fetchRequest, sendFormDataRequest } from "./fetchHelper";

const endpoint = "/api/organisations";

export interface OrganisationSearchResponse {
  id: number;
  name: string;
  country: string;
  town: string;
  type: string;
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

export const organisationApiService = {
  search,
  upload,
  pollTask,
};
