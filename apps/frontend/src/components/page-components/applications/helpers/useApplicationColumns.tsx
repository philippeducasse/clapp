"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Application } from "@/interfaces/entities/Application";
import { Pencil, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";
import { StatusBadge } from "@/components/common/StatusBadge";
import _ from "lodash"

const useApplicationColumns = (): ColumnDef<Application>[] => {
  const router = useRouter();

  const onEdit = (id: string) => {
    router.push(`/applications/${id}/edit`);
  };
  return [
    {
      accessorKey: "organisation.name",
      header: "Organisation",
      size: 200,
      cell: ({ row }) => {
        const application = row.original;
        return (
          <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
            <Link href={`/applications/${application.id}`}>{_.capitalize(application.organisation.name)}</Link>
          </div>
        );
      },
    },
    {
      accessorKey: "createdAt",
      header: getSortableHeader("Application date"),
      size: 110,
      cell: ({ row }) => {
        const date = row.original.createdAt;
        return (
          <div className="overflow-hidden text-ellipsis whitespace-nowrap ">
            <span>{new Date(date).toLocaleString()}</span>
          </div>
        );
      },
    },
    {
      accessorKey: "applicationStatus",
      header: getSortableHeader("Status"),
      size: 110,
      filterFn: (row, columnId, filterValue) => {
        if (!Array.isArray(filterValue) || filterValue.length === 0) return true;
        return filterValue.includes(row.getValue(columnId));
      },
      cell: ({ row }) => {
        const application = row.original;
        return <StatusBadge status={application.applicationStatus} />;
      },
    },
    {
      accessorKey: "organisationType",
      header: "Organisation type",
      size: 110,
       cell: ({ row }) => {
        return (
            <span>{_.capitalize(row.original.organisationType)}</span>
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
            <Button variant="outline" size="icon" className="size-8 hover:text-red-500">
              <Trash />
            </Button>
          </div>
        );
      },
    },
  ];
};

export { useApplicationColumns };
