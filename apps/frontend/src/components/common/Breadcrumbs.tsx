"use client";

import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Home } from "lucide-react";
import React, { useState } from "react";

const Breadcrumbs = () => {
  const [section, setSection] = useState({ link: "/festivals", label: "Festivals" });
  const [entity, setEntity] = useState({ link: `festivals/1`, label: "Festival Name" });
  const [action, setAction] = useState("Edit");

  return (
    <Breadcrumb>
      <BreadcrumbList>
        <BreadcrumbItem>
          <BreadcrumbLink href="/">
            <Home className="text-emerald-600" />
          </BreadcrumbLink>
        </BreadcrumbItem>
        <BreadcrumbSeparator />
        <BreadcrumbItem>
          <BreadcrumbLink className="text-base" href={section.link}>
            {section.label}
          </BreadcrumbLink>
        </BreadcrumbItem>
        {entity && (
          <>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink className="text-base" href={section.link}>
                {entity.label}
              </BreadcrumbLink>
            </BreadcrumbItem>
          </>
        )}
        {action && (
          <>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink className="text-base" href={section.link}>
                {action}
              </BreadcrumbLink>
            </BreadcrumbItem>
          </>
        )}
      </BreadcrumbList>
    </Breadcrumb>
  );
};

export default Breadcrumbs;
