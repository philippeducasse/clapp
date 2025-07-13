"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Festival } from "@/interfaces/Festival";
import { MoreHorizontal, Pencil } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import Link from "next/link";
export const columns: ColumnDef<Festival>[] = [
  {
    accessorKey: "festivalName",
    header: "Name",
    cell: ({ row }) => {
      const festival = row.original;
      return (
        <div className="overflow-hidden text-ellipsis whitespace-nowrap">
          <Link
            // className="underline text-slate-400 hover:text-slate-500"
            href={`/festivals/${festival.id}`}
          >
            {festival.festivalName}
          </Link>
        </div>
      );
    },
  },
  {
    accessorKey: "country",
    header: "Country",
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
    accessorKey: "dateString",
    header: "Date",
  },
  // {
  //   accessorKey: "startDate",
  //   header: "Date",
  //   cell: ({ row }) => {
  //     const date = new Date(row.getValue("startDate"));
  //     const formattedDate = date.toLocaleDateString();
  //     return <div>{formattedDate}</div>;
  //   },
  // },
  {
    header: "Actions",
    id: "actions",
    cell: ({ row }) => {
      const festival = row.original;

      return (
        <>
          <Button variant="secondary" size="icon" className="size-8">
            <Pencil />
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="h-8 w-8 p-0">
                <span className="sr-only">Open menu</span>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Actions</DropdownMenuLabel>
              <DropdownMenuItem onClick={() => navigator.clipboard.writeText(String(festival.id))}>
                Copy festival ID
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>View Festival details</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </>
      );
    },
  },
];
