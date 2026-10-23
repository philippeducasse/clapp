import { applicationApiService } from "@/api/applicationApiService";
import { ApplicationType } from "@/interfaces/entities/Festival";

export const RECENT_APPLICATION_MONTHS = 6;

/** Local date `months` before `now`, as YYYY-MM-DD (the format of `applicationDate`). */
export const getDateMonthsAgo = (months: number, now: Date = new Date()): string => {
  const date = new Date(now.getFullYear(), now.getMonth() - months, now.getDate());
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
};

interface WarningInput {
  organisationName?: string;
  applicationType?: string;
  hasRecentApplication: boolean;
}

/** Reasons to double-check before sending an application by email. */
export const buildEmailApplicationWarnings = ({
  organisationName,
  applicationType,
  hasRecentApplication,
}: WarningInput): string[] => {
  const name = organisationName || "this organisation";
  const warnings: string[] = [];
  if (applicationType === ApplicationType.FORM) {
    warnings.push(`${name} takes applications through a form, not by email.`);
  }
  if (hasRecentApplication) {
    warnings.push(
      `You already applied to ${name} in the last ${RECENT_APPLICATION_MONTHS} months.`,
    );
  }
  return warnings;
};

/** Whether the user has applied to this organisation in the last 6 months. */
export const hasRecentApplication = async (
  organisationType: string,
  organisationId: number,
): Promise<boolean> => {
  const response = await applicationApiService.getAll({
    limit: 1,
    filters: {
      organisationType,
      organisation: organisationId,
      appliedAfter: getDateMonthsAgo(RECENT_APPLICATION_MONTHS),
    },
  });
  return response.count > 0;
};
