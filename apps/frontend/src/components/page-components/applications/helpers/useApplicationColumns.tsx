"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Application } from "@/interfaces/entities/Application";
import { Pencil, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";
import { capitalize } from "lodash";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/common/StatusBadge";

const useApplicationColumns = (): ColumnDef<Application>[] => {
  const router = useRouter();

  const onEdit = (id: string) => {
    router.push(`/applications/${id}/edit`);
  };
  return [
    {
      accessorKey: "emailSubject",
      header: "Application",
      size: 200,
      cell: ({ row }) => {
        const application = row.original;
        return (
          <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
            <Link href={`/applications/${application.id}`}>
              {application.emailSubject}
            </Link>
          </div>
        );
      },
    },
    {
      accessorKey: "createdAt",
      header: "Application date",
      size: 110,
    },
    {
      accessorKey: "applicationStatus",
      header: getSortableHeader("Status"),
      size: 110,
      cell: ({ row }) => {
        const application = row.original;
        return <StatusBadge status={application.applicationStatus} />;
      },
    },
    {
      accessorKey: "organisationType",
      header: "Organisation type",
      size: 110,
    },
    {
      accessorKey: "organisation.name",
      header: "Organisation",
      size: 200,
      cell: ({ row }) => {
        const application = row.original;
        return (
          <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
            <Link
              href={`/${application.organisationType.toLowerCase()}s/${
                application.organisation.id
              }`}
            >
              {application.organisation?.name}
            </Link>
          </div>
        );
      },
    },

    {
      header: "Actions",
      id: "actions",
      cell: ({ row }) => {
        const application = row.original;
        return (
          <div className="flex gap-2 align-middle">
            <Button
              variant="outline"
              size="icon"
              className="size-8 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
              onClick={() => onEdit(String(application.id))}
            >
              <Pencil />
            </Button>
            <Button
              variant="outline"
              size="icon"
              className="size-8 hover:text-red-500"
            >
              <Trash />
            </Button>
          </div>
        );
      },
    },
  ];
};

export { useApplicationColumns };
