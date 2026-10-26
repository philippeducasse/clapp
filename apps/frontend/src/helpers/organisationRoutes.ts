import { OrganisationType } from "@/interfaces/Enums";

/** Frontend route (and API path segment) per organisation type. */
export const ORGANISATION_ROUTES: Record<OrganisationType, string> = {
  [OrganisationType.FESTIVAL]: "/festivals",
  [OrganisationType.VENUE]: "/venues",
  [OrganisationType.RESIDENCY]: "/residencies",
};

export const ORGANISATION_TYPE_LABELS: Record<OrganisationType, string> = {
  [OrganisationType.FESTIVAL]: "Festival",
  [OrganisationType.VENUE]: "Venue",
  [OrganisationType.RESIDENCY]: "Residency",
};

// Details only some organisation types have; dropped when converting to a type without them.
// Mirrors the backend models (organisations/{festivals,residencies,venues}/models.py).
const TYPE_DETAILS: Record<OrganisationType, string[]> = {
  [OrganisationType.FESTIVAL]: ["festival type", "dates", "application details"],
  [OrganisationType.RESIDENCY]: ["dates", "application details"],
  [OrganisationType.VENUE]: ["venue type", "contacted status"],
};

/** Details of a `from` organisation that a `to` organisation can't keep. */
export const getDetailsLostOnConversion = (
  from: OrganisationType,
  to: OrganisationType,
): string[] => TYPE_DETAILS[from].filter((detail) => !TYPE_DETAILS[to].includes(detail));
