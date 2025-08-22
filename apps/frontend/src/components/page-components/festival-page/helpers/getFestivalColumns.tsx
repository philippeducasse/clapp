"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Festival } from "@/interfaces/Festival";
import { Pencil, Trash } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";

const getFestivalColumns = (onEdit: (id: string) => void): ColumnDef<Festival>[] => {
  return [
    {
      accessorKey: "festivalName",
      header: getSortableHeader("Name"),
      cell: ({ row }) => {
        const festival = row.original;
        return (
          <div className="overflow-hidden text-ellipsis whitespace-nowrap">
            <Link href={`/festivals/${festival.id}`}>{festival.festivalName}</Link>
          </div>
        );
      },
    },
    {
      accessorKey: "country",
      header: getSortableHeader("Country"),
    },
    {
      accessorKey: "websiteUrl",
      header: "Website",
      size: 200,

      cell: ({ row }) => {
        const festival = row.original;
        return (
          <div className="overflow-hidden text-ellipsis whitespace-nowrap">
            <Link
              // className="underline text-slate-400 hover:text-slate-500"
              href={festival.websiteUrl ?? "#"}
              target="_blank"
              title={festival.websiteUrl}
            >
              {festival.websiteUrl}
            </Link>
          </div>
        );
      },
    },
    {
      accessorKey: "approximateDate",
      header: "Date",
    },
    {
      header: "Actions",
      id: "actions",
      cell: ({ row }) => {
        const festival = row.original;

        return (
          <div className="flex gap-2 align-middle">
            <Button variant="secondary" size="icon" className="size-8" onClick={() => onEdit(String(festival.id))}>
              <Pencil />
            </Button>
            <Button variant="secondary" size="icon" className="size-8">
              <Trash />
            </Button>
          </div>
        );
      },
    },
  ];
};

export { getFestivalColumns };
