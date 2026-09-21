import { sendFormDataRequest } from "./fetchHelper";

export interface BugReport {
  message: string;
  attachments?: File[];
}

const endpoint = "/api/support";

const reportBug = async (bugReport: BugReport): Promise<{ id: number }> => {
  const { attachments, ...reportData } = bugReport;

  if (attachments && attachments.length > 0) {
    return await sendFormDataRequest(
      `${endpoint}/bugs`,
      reportData,
      attachments,
      "attachments",
      "POST",
      "Bug report submitted successfully. Thank you for your feedback!",
    );
  }

  return await sendFormDataRequest(
    `${endpoint}/bugs`,
    reportData,
    undefined,
    undefined,
    "POST",
    "Bug report submitted successfully. Thank you for your feedback!",
  );
};

export const supportApiService = {
  reportBug,
};
