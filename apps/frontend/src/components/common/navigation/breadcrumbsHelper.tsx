import React from "react";
import { RootState } from "@/redux/store";
import { selectFestival } from "@/redux/slices/festivalSlice";
import { selectVenue } from "@/redux/slices/venueSlice";
import { selectResidency } from "@/redux/slices/residencySlice";
import { selectApplication } from "@/redux/slices/applicationSlice";
import { selectProfile } from "@/redux/slices/authSlice";

export interface Breadcrumb {
  path: string;
  label: React.ReactNode;
}

export interface EntityData {
  id?: number;
  name?: string;
  organisationName?: string;
}

export type EntityType =
  | "festivals"
  | "venues"
  | "residencies"
  | "applications"
  | "profile"
  | "help"
  | "report-bug"
  | "upload"
  | "preferences"
  | "dashboard";

const ENTITY_LABELS: Record<EntityType, string> = {
  festivals: "Festivals",
  venues: "Venues",
  residencies: "Residencies",
  applications: "Applications",
  profile: "Profile",
  help: "Help",
  "report-bug": "Report Bug",
  upload: "Upload",
  preferences: "Preferences",
  dashboard: "Dashboard",
};

export const extractEntityId = (pathname: string, entityType: EntityType): number | undefined => {
  if (!pathname.includes(`/${entityType}/`)) return undefined;
  const pathSegments = pathname.split("/").filter(Boolean);
  const index = pathSegments.indexOf(entityType);
  return index !== -1 && index + 1 < pathSegments.length
    ? Number(pathSegments[index + 1])
    : undefined;
};

export const detectEntityType = (pathname: string): EntityType => {
  const pathSegments = pathname.split("/").filter(Boolean);
  const firstSegment = pathSegments[0];
  const secondSegment = pathSegments[1];
  const thirdSegment = pathSegments[2];

  // Handle /profile/edit/preferences specifically
  if (firstSegment === "profile" && secondSegment === "edit" && thirdSegment === "preferences") {
    return "preferences";
  }

  // Default behavior based on first segment
  switch (firstSegment) {
    case "festivals":
      return "festivals";
    case "venues":
      return "venues";
    case "residencies":
      return "residencies";
    case "applications":
      return "applications";
    case "profile":
      return "profile";
    case "help":
      return "help";
    case "report-bug":
      return "report-bug";
    case "upload":
      return "upload";
    case "preferences":
      return "preferences";
    default:
      return "dashboard";
  }
};

export const getEntityData = (
  state: RootState,
  entityType: EntityType | null,
  entityId: number | undefined
): EntityData | null => {
  if (!entityType || !entityId) return null;

  switch (entityType) {
    case "festivals": {
      const entity = selectFestival(state, entityId);
      return entity ? { id: entity.id, name: entity.name } : null;
    }
    case "venues": {
      const entity = selectVenue(state, entityId);
      return entity ? { id: entity.id, name: entity.name } : null;
    }
    case "residencies": {
      const entity = selectResidency(state, entityId);
      return entity ? { id: entity.id, name: entity.name } : null;
    }
    case "applications": {
      const entity = selectApplication(state, entityId);
      return entity ? { id: entity.id, organisationName: entity.organisation.name } : null;
    }
    case "profile": {
      const entity = selectProfile(state);
      return entity ? { id: entity.id, name: entity.email } : null;
    }
    default:
      return { id: undefined, name: "Dashboard" };
  }
};

export const getEntityPath = (entityType: EntityType, entityId?: number): string => {
  if (entityId) {
    return `/${entityType}/${entityId}`;
  } else {
    return `/${entityType}`;
  }
};

export const getEntityDisplayName = (entityData: EntityData | null): string => {
  if (!entityData) return "";
  return entityData.organisationName ?? entityData.name ?? "";
};

export const extractAction = (pathname: string): "create" | "edit" | "apply" | null => {
  const pathSegments = pathname.split("/").filter(Boolean);
  if (pathSegments.includes("create")) return "create";
  if (pathSegments.includes("edit")) return "edit";
  if (pathSegments.includes("apply")) return "apply";
  return null;
};

export const buildStandardEntityBreadcrumbs = (
  breadcrumbs: Breadcrumb[],
  entityType: EntityType,
  entityData: EntityData | null,
  pathname: string,
  action: "create" | "edit" | "apply" | null
): Breadcrumb[] => {
  const result = [...breadcrumbs];

  try {
    // Handle special pages
    if (entityType === "help") {
      result.push({
        path: "/help",
        label: <span>{ENTITY_LABELS.help}</span>,
      });
      if (pathname.includes("/importing-organizations")) {
        result.push({
          path: pathname,
          label: <span>Importing Organizations</span>,
        });
      }
      return result;
    }

    if (entityType === "report-bug") {
      result.push({
        path: pathname,
        label: <span>{ENTITY_LABELS["report-bug"]}</span>,
      });
      return result;
    }

    if (entityType === "upload") {
      result.push({
        path: pathname,
        label: <span>{ENTITY_LABELS.upload}</span>,
      });
      return result;
    }

    if (entityType === "preferences") {
      result.push({
        path: "/profile/edit",
        label: <span>Edit Profile</span>,
      });
      result.push({
        path: pathname,
        label: <span>{ENTITY_LABELS.preferences}</span>,
      });
      return result;
    }

    // Handle standard entity pages
    result.push({
      path: `/${entityType}`,
      label: <span>{ENTITY_LABELS[entityType]}</span>,
    });

    if (entityType == "profile" && action) {
      result.push({
        path: pathname,
        label: <span>Edit</span>,
      });
    }

    if (entityData?.id) {
      const entityPath = getEntityPath(entityType, entityData?.id);
      result.push({
        path: entityPath,
        label: <span>{getEntityDisplayName(entityData)}</span>,
      });

      if (action && action !== "create") {
        result.push({
          path: pathname,
          label: <span>{action.charAt(0).toUpperCase() + action.slice(1)}</span>,
        });
      }
    } else if (action === "create") {
      result.push({
        path: pathname,
        label: <span>Create</span>,
      });
    }
  } catch (error) {
    console.error("Error building breadcrumbs:", error);
  }

  return result;
};

export const buildApplicationBreadcrumbs = (
  breadcrumbs: Breadcrumb[],
  entityData: EntityData | null,
  pathname: string,
  action: "create" | "edit" | "apply" | null
): Breadcrumb[] => {
  const result = [...breadcrumbs];

  result.push({
    path: "/applications",
    label: <span>{ENTITY_LABELS.applications}</span>,
  });

  if (entityData?.id) {
    const entityPath = getEntityPath("applications", entityData.id);
    result.push({
      path: entityPath,
      label: <span>{getEntityDisplayName(entityData)}</span>,
    });

    if (action === "edit") {
      result.push({
        path: pathname,
        label: <span>Edit</span>,
      });
    }
  } else if (action === "create") {
    result.push({
      path: pathname,
      label: <span>Create</span>,
    });
  }

  return result;
};
