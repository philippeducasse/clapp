"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Application } from "@/interfaces/entities/Application";
import { Pencil, Trash, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";

const useApplicationColumns = (): ColumnDef<Application>[] => {
  const router = useRouter();

  const onEdit = (id: string) => {
    router.push(`/applications/${id}/edit`);
  };
  return [
    {
      accessorKey: "application.organisationId",
      header: "Festival",
      size: 200,
      cell: ({ row }) => {
        const application = row.original;
        console.log(application)
        return (
          <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
            <Link href={`/applications/${application.id}`}>{application.organisationId}</Link>
          </div>
        );
      },
    },
    {
      accessorKey: "emailSubject",
      header: "Message",
      size: 200,
    },
    {
      header: "Actions",
      id: "actions",
      cell: ({ row }) => {
        const venue = row.original;
        // const applyRoute = venue.applied ? `/application/${1}` : `/venues/${venue.id}/apply`; // find way to reference application id
        const onApply = () => {
          // router.push(applyRoute);
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
