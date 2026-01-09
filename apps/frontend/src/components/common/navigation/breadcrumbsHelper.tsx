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

export type EntityType = "festivals" | "venues" | "residencies" | "applications" | "profile";

const ENTITY_LABELS: Record<EntityType, string> = {
  festivals: "Festivals",
  venues: "Venues",
  residencies: "Residencies",
  applications: "Applications",
  profile: "Profile",
};

export const extractEntityId = (pathname: string, entityType: EntityType): number | undefined => {
  if (!pathname.includes(`/${entityType}/`)) return undefined;
  const pathSegments = pathname.split("/").filter(Boolean);
  const index = pathSegments.indexOf(entityType);
  return index !== -1 && index + 1 < pathSegments.length
    ? Number(pathSegments[index + 1])
    : undefined;
};

export const detectEntityType = (pathname: string): EntityType | null => {
  if (pathname.includes("/festivals")) return "festivals";
  if (pathname.includes("/venues")) return "venues";
  if (pathname.includes("/residencies")) return "residencies";
  if (pathname.includes("/applications")) return "applications";
  if (pathname.includes("/profile")) return "profile";
  return null;
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
      return null;
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
