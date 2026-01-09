"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Residency } from "@/interfaces/entities/Residency";
import { Pencil, Trash, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";
import { TagBadge } from "@/components/common/TagBadge";
import { useCallback, useMemo } from "react";
import { Application } from "@/interfaces/entities/Application";

interface UseResidencyColumnsProps {
  onDeleteClick: (id: number) => void;
}

const useResidencyColumns = ({
  onDeleteClick,
}: UseResidencyColumnsProps): ColumnDef<Residency>[] => {
  const router = useRouter();

  const onEdit = useCallback(
    (id: string) => {
      router.push(`/residencies/${id}/edit`);
    },
    [router]
  );

  return useMemo(
    () => [
      {
        accessorKey: "name",
        header: getSortableHeader("Name"),
        size: 100,
        cell: ({ row }) => {
          const residency = row.original;
          return (
            <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
              <Link href={`/residencies/${residency.id}`}>{residency.name}</Link>
            </div>
          );
        },
      },
      {
        accessorKey: "currentYearApplications",
        header: getSortableHeader("Applied"),
        size: 70,
        filterFn: (row, _columnId, filterValue) => {
          if (filterValue === undefined) return true;
          const hasApplication = !!(row.original?.currentYearApplication as Application)?.id;
          return filterValue === "APPLIED" ? hasApplication : !hasApplication;
        },
        cell: ({ row }) => {
          const application = row.original?.currentYearApplication as Application;
          return (
            <div className="overflow-hidden text-ellipsis whitespace-nowrap text-sky-600 font-semibold hover:text-sky-500">
              <Link href={`/applications/${application.id}`}>{application.applicationDate}</Link>
            </div>
          );
        },
      },
      {
        accessorKey: "tag",
        header: getSortableHeader("Tag"),
        size: 50,
        filterFn: (row, columnId, filterValue) => {
          if (!Array.isArray(filterValue) || filterValue.length === 0) return true;
          return filterValue.includes(row.getValue(columnId));
        },
        cell: ({ row }) => {
          const tag = row.original?.tag;
          return <TagBadge tag={tag} />;
        },
      },
      {
        accessorKey: "country",
        header: getSortableHeader("Country"),
        size: 70,
      },
      {
        accessorKey: "websiteUrl",
        header: "Website",
        size: 100,
        cell: ({ row }) => {
          const residency = row.original;
          return (
            <div className="overflow-hidden text-ellipsis whitespace-nowrap text-sky-600 font-semibold hover:text-sky-500">
              <Link href={residency.website ?? "#"} target="_blank" title={residency.websiteUrl}>
                {residency.websiteUrl}
              </Link>
            </div>
          );
        },
      },
      {
        accessorKey: "approximateDate",
        header: "Date",
        size: 100,
      },
      {
        header: "Actions",
        id: "actions",
        size: 75,
        cell: ({ row }) => {
          const residency = row.original;
          const applyRoute = `/residencies/${residency.id}/apply`;
          const onApply = () => {
            router.push(applyRoute);
          };
          return (
            <div className="flex gap-2 align-middle">
              <Button
                variant="outline"
                size="icon"
                className="size-8 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
                onClick={() => onEdit(String(residency.id))}
              >
                <Pencil />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="size-8 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
                onClick={onApply}
              >
                <Send />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="size-8 hover:text-red-500"
                onClick={() => onDeleteClick(residency.id)}
              >
                <Trash />
              </Button>
            </div>
          );
        },
      },
    ],
    [onDeleteClick, onEdit, router]
  );
};

export { useResidencyColumns };
