"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Venue } from "@/interfaces/entities/Venue";
import { Pencil, Trash, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";
import { capitalizeFirst } from "@/utils/stringUtils";
import { TagBadge } from "@/components/common/TagBadge";
import { useCallback, useMemo } from "react";

interface UseVenueColumnsProps {
  onDeleteClick: (id: number) => void;
}

const useVenueColumns = ({ onDeleteClick }: UseVenueColumnsProps): ColumnDef<Venue>[] => {
  const router = useRouter();

  const onEdit = useCallback(
    (id: string) => {
      router.push(`/venues/${id}/edit`);
    },
    [router],
  );

  return useMemo(
    () => [
      {
        accessorKey: "name",
        header: getSortableHeader("Name"),
        size: 100,
        cell: ({ row }) => {
          const venue = row.original;
          return (
            <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-primary hover:text-primary/80">
              <Link href={`/venues/${venue.id}`}>{venue.name}</Link>
            </div>
          );
        },
      },
      {
        accessorKey: "tag",
        header: getSortableHeader("Tag"),
        size: 50,
        filterFn: (row, columnId, filterValue): boolean => {
          if (!Array.isArray(filterValue) || filterValue.length === 0) return true;
          return filterValue.includes(row.getValue(columnId));
        },
        cell: ({ row }) => {
          const tag = row.original?.tag;
          return <TagBadge tag={tag} />;
        },
      },
      {
        accessorKey: "venueType",
        header: getSortableHeader("Type"),
        size: 70,
        cell: ({ row }) => capitalizeFirst(row.original.venueType),
      },
      {
        accessorKey: "country",
        header: getSortableHeader("Country"),
        size: 70,
      },
      {
        accessorKey: "contacted",
        header: getSortableHeader("Contacted"),
        size: 70,
        filterFn: (row, _columnId, filterValue): boolean => {
          if (filterValue === undefined) return true;
          const contacted = !!row.original?.contacted;
          return filterValue === "CONTACTED" ? contacted : !contacted;
        },
        cell: ({ row }) => {
          const contacted = row.original?.contacted;
          return <span>{contacted ? "Yes" : "No"}</span>;
        },
      },
      {
        accessorKey: "websiteUrl",
        header: "Website",
        size: 100,
        cell: ({ row }) => {
          const venue = row.original;
          return (
            <div className="overflow-hidden text-ellipsis whitespace-nowrap text-sky-600 font-semibold hover:text-sky-500">
              <Link href={venue.websiteUrl ?? "#"} target="_blank" title={venue.websiteUrl}>
                {venue.websiteUrl}
              </Link>
            </div>
          );
        },
      },
      {
        header: "Actions",
        id: "actions",
        size: 75,
        cell: ({ row }) => {
          const venue = row.original;
          const applyRoute = venue.applied ? `/application/${1}` : `/venues/${venue.id}/apply`; // find way to reference application id
          const onApply = () => {
            router.push(applyRoute);
          };
          return (
            <div className="flex gap-2 align-middle">
              <Button
                variant="outline"
                size="icon"
                className="size-8 text-primary hover:text-primary/80"
                onClick={() => onEdit(String(venue.id))}
              >
                <Pencil />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="size-8 text-primary hover:text-primary/80"
                onClick={onApply}
              >
                <Send />
              </Button>
              <Button
                variant="outline"
                size="icon"
                className="size-8 hover:text-red-500"
                onClick={() => onDeleteClick(venue.id)}
              >
                <Trash />
              </Button>
            </div>
          );
        },
      },
    ],
    [onDeleteClick, onEdit, router],
  );
};

export { useVenueColumns };
