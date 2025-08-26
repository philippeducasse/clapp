"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Festival } from "@/interfaces/Festival";
import { Pencil, Trash, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";

const getFestivalColumns = (onEdit: (id: string) => void): ColumnDef<Festival>[] => {
  return [
    {
      accessorKey: "festivalName",
      header: getSortableHeader("Name"),
      size: 200,
      cell: ({ row }) => {
        const festival = row.original;
        return (
          <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
            <Link href={`/festivals/${festival.id}`}>{festival.festivalName}</Link>
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
        const festival = row.original;
        return (
          <div className="overflow-hidden text-ellipsis whitespace-nowrap text-sky-600 font-semibold hover:text-sky-500">
            <Link href={festival.websiteUrl ?? "#"} target="_blank" title={festival.websiteUrl}>
              {festival.websiteUrl}
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
        const festival = row.original;

        return (
          <div className="flex gap-2 align-middle">
            <Button
              variant="secondary"
              size="icon"
              className="size-8 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
              onClick={() => onEdit(String(festival.id))}
            >
              <Pencil />
            </Button>
            <Button
              variant="secondary"
              size="icon"
              className="size-8 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
            >
              <Mail />
            </Button>
            <Button variant="secondary" size="icon" className="size-8 hover:text-red-500">
              <Trash />
            </Button>
          </div>
        );
      },
    },
  ];
};

export { getFestivalColumns };
