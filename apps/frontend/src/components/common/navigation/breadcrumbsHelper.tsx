import React from "react";
import { RootState } from "@/redux/store";
import { selectFestival } from "@/redux/slices/festivalSlice";
import { selectVenue } from "@/redux/slices/venueSlice";
import { selectResidency } from "@/redux/slices/residencySlice";
import { selectApplication } from "@/redux/slices/applicationSlice";
import { selectProfile } from "@/redux/slices/authSlice";
import { capitalizeFirst } from "@/utils/stringUtils";
import { Action } from "@/interfaces/Enums";

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
  const entityName = pathSegments[0] as EntityType;

  return entityName ?? "dashboard";
};

export const getEntityData = (
  state: RootState,
  entityType: EntityType | null,
  entityId: number | undefined,
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

export const extractAction = (pathname: string): Action | null => {
  const pathSegments = pathname.split("/").filter(Boolean);
  if (pathSegments.includes("create")) return Action.CREATE;
  if (pathSegments.includes("edit")) return Action.EDIT;
  if (pathSegments.includes("apply")) return Action.APPLY;
  return null;
};

const SPECIAL_PAGES_CONFIG: Partial<
  Record<EntityType, { breadcrumbs?: Breadcrumb[]; subPages?: Record<string, string> }>
> = {
  help: {
    breadcrumbs: [{ path: "/help", label: "Help" }],
    subPages: { "/importing-organizations": "Importing Organizations" },
  },
  "report-bug": {
    breadcrumbs: [{ path: null as any, label: "Report Bug" }],
  },
  upload: {
    breadcrumbs: [{ path: null as any, label: "Upload" }],
  },
  preferences: {
    breadcrumbs: [
      { path: "/profile/edit", label: "Edit Profile" },
      { path: null as any, label: "Preferences" },
    ],
  },
};

const addActionBreadcrumb = (
  breadcrumbs: Breadcrumb[],
  action: Action | null,
  pathname: string,
): void => {
  if (!action) return;

  if (action === Action.CREATE) {
    breadcrumbs.push({ path: pathname, label: "Create" });
  } else {
    breadcrumbs.push({
      path: pathname,
      label: capitalizeFirst(action),
    });
  }
};

export const buildStandardEntityBreadcrumbs = (
  breadcrumbs: Breadcrumb[],
  entityType: EntityType,
  entityData: EntityData | null,
  pathname: string,
  action: Action | null,
): Breadcrumb[] => {
  const result = [...breadcrumbs];

  try {
    // Handle special pages
    const config = SPECIAL_PAGES_CONFIG[entityType];
    if (config?.breadcrumbs) {
      config.breadcrumbs.forEach(({ path, label }) => {
        result.push({
          path: path || pathname,
          label: typeof label === "string" ? label : capitalizeFirst(entityType),
        });
      });

      // Check for sub-pages
      if (config.subPages) {
        Object.entries(config.subPages).forEach(([pathSegment, label]) => {
          if (pathname.includes(pathSegment)) {
            result.push({ path: pathname, label });
          }
        });
      }

      return result;
    }

    // Handle standard entity pages
    result.push({
      path: `/${entityType}`,
      label: capitalizeFirst(entityType),
    });

    if (entityType === "profile" && action) {
      result.push({
        path: pathname,
        label: "Edit",
      });
    }

    if (entityData?.id) {
      const entityPath = getEntityPath(entityType, entityData?.id);
      result.push({
        path: entityPath,
        label: getEntityDisplayName(entityData),
      });
      addActionBreadcrumb(result, action, pathname);
    } else if (action === Action.CREATE) {
      result.push({
        path: pathname,
        label: "Create",
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
  action: Action | null,
): Breadcrumb[] => {
  const result = [...breadcrumbs];

  result.push({
    path: "/applications",
    label: "Applications",
  });

  if (entityData?.id) {
    const entityPath = getEntityPath("applications", entityData.id);
    result.push({
      path: entityPath,
      label: getEntityDisplayName(entityData),
    });
    addActionBreadcrumb(result, action, pathname);
  } else if (action === Action.CREATE) {
    result.push({
      path: pathname,
      label: "Create",
    });
  }

  return result;
};
