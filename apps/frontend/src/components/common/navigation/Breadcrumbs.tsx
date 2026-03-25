"use client";
import React from "react";
import { useSelector } from "react-redux";
import { RootState } from "@/redux/store";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Home } from "lucide-react";
import { usePathname } from "next/navigation";
import {
  detectEntityType,
  getEntityData,
  extractAction,
  buildStandardEntityBreadcrumbs,
  buildApplicationBreadcrumbs,
  Breadcrumb as BreadcrumbType,
} from "./breadcrumbsHelper";

const Breadcrumbs = () => {
  const pathname = usePathname();

  const entityType = detectEntityType(pathname);

  const entityData = useSelector((state: RootState) => {
    if (!entityType) return null;

    const entityIdMatch = pathname.match(
      /\/(festivals|venues|residencies|applications|profile)\/(\d+)/,
    );
    const entityId = entityIdMatch ? Number(entityIdMatch[2]) : undefined;

    return getEntityData(state, entityType, entityId);
  });

  const action = extractAction(pathname);

  const buildBreadcrumbs = (): BreadcrumbType[] => {
    const breadcrumbs: BreadcrumbType[] = [
      { path: "/", label: <Home className="text-emerald-600 dark:text-emerald-400" /> },
    ];

    if (!entityType) return breadcrumbs;

    if (entityType === "applications") {
      return buildApplicationBreadcrumbs(breadcrumbs, entityData, pathname, action);
    } else {
      return buildStandardEntityBreadcrumbs(breadcrumbs, entityType, entityData, pathname, action);
    }
  };

  const breadcrumbs = buildBreadcrumbs();
  return (
    <Breadcrumb>
      <BreadcrumbList>
        {breadcrumbs.map((crumb, index) => (
          <React.Fragment key={crumb.path}>
            {index > 0 && <BreadcrumbSeparator />}
            <BreadcrumbItem>
              {index === breadcrumbs.length - 1 ? (
                <span className="text-base">{crumb.label}</span>
              ) : (
                <BreadcrumbLink className="text-base" href={crumb.path}>
                  {crumb.label}
                </BreadcrumbLink>
              )}
            </BreadcrumbItem>
          </React.Fragment>
        ))}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

export default Breadcrumbs;
