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

const Breadcrumbs = () => {
  const pathname = usePathname();

  // Get data from Redux slices if needed
  const festival = useSelector((state: RootState) => state.festivals.selectedFestival);
  // const application = useSelector((state: RootState) => state.applications.currentApplication);

  // Determine which entity we're dealing with
  let entityName = "";
  let entityPath = "";

  if (pathname.includes("/festivals/")) {
    entityName = festival?.festivalName ?? "Festival";
    entityPath = `/festivals/${festival?.id ?? ""}`;
  } else if (pathname.includes("/applications/")) {
    // entityName = application?.name || "Application";
    // entityPath = `/applications/${application?.id || ""}`;
  }

  // Build breadcrumbs based on current route
  const buildBreadcrumbs = () => {
    const pathSegments = pathname.split("/").filter(Boolean);
    const breadcrumbs = [{ path: "/", label: <Home className="text-emerald-600" /> }];

    if (pathSegments.includes("festivals")) {
      breadcrumbs.push({ path: "/festivals", label: "Festivals" });

      if (festival?.id) {
        breadcrumbs.push({ path: entityPath, label: entityName });

        // Add action if we're on an edit/new page
        if (pathSegments.includes("edit")) {
          breadcrumbs.push({ path: pathname, label: "Edit" });
        } else if (pathSegments.includes("new")) {
          breadcrumbs.push({ path: pathname, label: "New" });
        }
      }
    }
    // else if (pathSegments.includes("applications")) {
    //   breadcrumbs.push({ path: "/applications", label: "Applications" });

    //   if (application?.id) {
    //     breadcrumbs.push({ path: entityPath, label: entityName });

    //     // Add action if we're on an edit/new page
    //     if (pathSegments.includes("edit")) {
    //       breadcrumbs.push({ path: pathname, label: "Edit" });
    //     } else if (pathSegments.includes("new")) {
    //       breadcrumbs.push({ path: pathname, label: "New" });
    //     }
    //   }
    // }

    return breadcrumbs;
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
