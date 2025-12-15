"use client";
import { ColumnDef } from "@tanstack/react-table";
import { Application, ApplicationStatus } from "@/interfaces/entities/Application";
import { Pencil, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";
import { StatusBadge } from "@/components/common/StatusBadge";
import { formatDate } from "@/utils/stringUtils";
import { capitalizeFirst } from "@/utils/stringUtils";
import { useCallback, useMemo } from "react";
import { StatusDropdown } from "@/components/common/table/StatusDropdown";

interface UseApplicationColumnsProps {
  onDeleteClick: (id: number) => void;
  onStatusChange: (id: number, status: ApplicationStatus) => void;
}

const useApplicationColumns = ({
  onDeleteClick,
  onStatusChange,
}: UseApplicationColumnsProps): ColumnDef<Application>[] => {
  const router = useRouter();

  const onEdit = useCallback(
    (id: string) => {
      router.push(`/applications/${id}/edit`);
    },
    [router]
  );

  return useMemo(
    () => [
      {
        accessorKey: "organisation.name",
        header: "Organisation",
        size: 200,
        cell: ({ row }) => {
          const application = row.original;
          return (
            <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
              <Link href={`/applications/${application.id}`}>
                {capitalizeFirst(application.organisation.name)}
              </Link>
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
              <span>{formatDate(date)}</span>
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
          return <StatusBadge status={application.status} />;
        },
      },
      {
        accessorKey: "organisationType",
        header: "Organisation type",
        size: 110,
        cell: ({ row }) => {
          return <span>{capitalizeFirst(row.original.organisationType)}</span>;
        },
      },
      {
        header: "Actions",
        id: "actions",
        size: 120,
        cell: ({ row }) => {
          const application = row.original;
          return (
            <div className="flex gap-2">
              <StatusDropdown
                entityId={application.id as number}
                onStatusChange={onStatusChange}
              />
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
                onClick={() => onDeleteClick(application.id as number)}
              >
                <Trash />
              </Button>
            </div>
          );
        },
      },
    ],
    [onEdit, onDeleteClick, onStatusChange]
  );
};

export { useApplicationColumns };
