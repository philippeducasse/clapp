"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Residency } from "@/interfaces/entities/Residency";
import { Pencil, Trash, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";

const useResidencyColumns = (): ColumnDef<Residency>[] => {
  const router = useRouter();

  const onEdit = (id: string) => {
    router.push(`/residencies/${id}/edit`);
  };
  return [
    {
      accessorKey: "name",
      header: getSortableHeader("Name"),
      size: 200,
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
      accessorKey: "country",
      header: getSortableHeader("Country"),
      size: 100,
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
            <Button variant="outline" size="icon" className="size-8 hover:text-red-500">
              <Trash />
            </Button>
          </div>
        );
      },
    },
  ];
};

export { useResidencyColumns };
