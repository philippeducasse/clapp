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
import { selectFestival } from "@/redux/slices/festivalSlice";
import { selectApplication } from "@/redux/slices/applicationSlice";

const Breadcrumbs = () => {
  const pathname = usePathname();

  // Extract IDs from URL path
  const pathSegments = pathname.split("/").filter(Boolean);
  const festivalId = pathname.includes("/festivals/") ? Number(pathSegments[1]) : undefined;
  const applicationId = pathname.includes("/applications/") ? Number(pathSegments[1]) : undefined;

  // Get data from Redux slices using selectors
  const festival = useSelector((state: RootState) =>
    festivalId ? selectFestival(state, festivalId) : undefined
  );
  const application = useSelector((state: RootState) =>
    applicationId ? selectApplication(state, applicationId) : undefined
  );

  // Determine which entity we're dealing with
  let entityName = "";
  let entityPath = "";

  if (pathname.includes("/festivals/") && festival) {
    entityName = festival.name ?? "Festival";
    entityPath = `/festivals/${festival.id}`;
  } else if (pathname.includes("/applications/") && application) {
    entityName = application.emailSubject ?? `Application for ${typeof application.organisation === 'object' ? application.organisation.name : 'Unknown'}`;
    entityPath = `/applications/${application.id}`;
  }

  // Build breadcrumbs based on current route
  const buildBreadcrumbs = () => {
    const breadcrumbs = [
      { path: "/", label: <Home className="text-emerald-600 dark:text-emerald-400" /> },
    ];

    if (pathSegments.includes("festivals")) {
      breadcrumbs.push({ path: "/festivals", label: <span>Festivals</span> });

      if (festival?.id) {
        breadcrumbs.push({ path: entityPath, label: <span>{entityName}</span> });

        // Add action if we're on an edit/new page
        if (pathSegments.includes("edit")) {
          breadcrumbs.push({ path: pathname, label: <span>Edit</span> });
        } else if (pathSegments.includes("apply")) {
          breadcrumbs.push({ path: pathname, label: <span>Apply</span> });
        }
      } else if (pathSegments.includes("create")) {
        breadcrumbs.push({ path: pathname, label: <span>Create</span> });
      }
    } else if (pathSegments.includes("applications")) {
      breadcrumbs.push({ path: "/applications", label: <span>Applications</span> });

      if (application?.id) {
        breadcrumbs.push({ path: entityPath, label: <span>entityName</span> });

        // Add action if we're on an edit/new page
        if (pathSegments.includes("edit")) {
          breadcrumbs.push({ path: pathname, label: <span>Edit</span> });
        } else if (pathSegments.includes("new")) {
          breadcrumbs.push({ path: pathname, label: <span>New</span> });
        }
      }
    }

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
