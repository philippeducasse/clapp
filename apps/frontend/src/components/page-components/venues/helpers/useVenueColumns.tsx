"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Venue } from "@/interfaces/entities/Venue";
import { Pencil, Trash, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";

const useVenueColumns = (): ColumnDef<Venue>[] => {
  const router = useRouter();

  const onEdit = (id: string) => {
    router.push(`/venues/${id}/edit`);
  };
  return [
    {
      accessorKey: "venueName",
      header: getSortableHeader("Name"),
      size: 200,
      cell: ({ row }) => {
        const venue = row.original;
        return (
          <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
            <Link href={`/venues/${venue.id}`}>{venue.venueName}</Link>
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
        const venue = row.original;
        return (
          <div className="overflow-hidden text-ellipsis whitespace-nowrap text-sky-600 font-semibold hover:text-sky-500">
            <Link
              href={venue.websiteUrl ?? "#"}
              target="_blank"
              title={venue.websiteUrl}
            >
              {venue.websiteUrl}
            </Link>
          </div>
        );
      },
    },
    {
      header: "Actions",
      id: "actions",
      cell: ({ row }) => {
        const venue = row.original;
        const applyRoute = venue.applied
          ? `/application/${1}`
          : `/venues/${venue.id}/apply`; // find way to reference application id
        const onApply = () => {
          router.push(applyRoute);
        };
        return (
          <div className="flex gap-2 align-middle">
            <Button
              variant="outline"
              size="icon"
              className="size-8 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
              onClick={() => onEdit(String(venue.id))}
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
            >
              <Trash />
            </Button>
          </div>
        );
      },
    },
  ];
};

export { useVenueColumns };
