"use client";
import { useState } from "react";
import { ColumnDef } from "@tanstack/react-table";
import { Festival } from "@/interfaces/entities/Festival";
import { Pencil, Trash, Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { getSortableHeader } from "@/components/common/table/getSortableHeader";
import { useRouter } from "next/navigation";
import _ from "lodash";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { festivalApiService } from "@/api/festivalApiService";
import { deleteFestival } from "@/redux/slices/festivalSlice";
import { useDispatch } from "react-redux";
import { TagBadge } from "@/components/common/TagBadge";
import { Application } from "@/interfaces/entities/Application";

const useFestivalColumns = (): ColumnDef<Festival>[] => {
  const router = useRouter();
  const [openDeleteModel, setOpenDeleteModal] = useState(false);
  const onEdit = (id: string) => {
    router.push(`/festivals/${id}/edit`);
  };
  const dispatch = useDispatch();

  const onConfirmDelete = async (id: number) => {
    await festivalApiService.remove(id as number);
    dispatch(deleteFestival(id as number));
  };

  return [
    {
      accessorKey: "name",
      header: getSortableHeader("Name"),
      size: 100,
      cell: ({ row }) => {
        const festival = row.original;
        return (
          <div className="overflow-hidden text-ellipsis font-semibold whitespace-nowrap text-emerald-700 hover:text-emerald-600 dark:text-emerald-400 dark:hover:text-emerald-300">
            <Link href={`/festivals/${festival.id}`}>{festival.name}</Link>
          </div>
        );
      },
    },
    {
      accessorKey: "currentYearApplications",
      header: getSortableHeader("Applied"),
      size: 70,
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
      accessorKey: "country",
      header: getSortableHeader("Country"),
      size: 70,
    },
    {
      accessorKey: "tag",
      header: getSortableHeader("Tag"),
      size: 50,
      cell: ({ row }) => {
        const tag = row.original?.tag;
        return <TagBadge tag={tag} />;
      },
    },
    {
      accessorKey: "festivalType",
      header: getSortableHeader("Type"),
      size: 70,
      cell: ({ row }) => _.capitalize(_.lowerCase(row.original.festivalType)),
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
        const applyRoute = festival.applied
          ? `/application/${1}`
          : `/festivals/${festival.id}/apply`; // find way to reference application id
        const onApply = () => {
          router.push(applyRoute);
        };
        return (
          <div className="flex gap-2 align-middle">
            <DeleteModal
              onConfirm={() => onConfirmDelete(festival.id)}
              open={openDeleteModel}
              onOpenChange={setOpenDeleteModal}
              itemName="Festival"
            />
            <Button
              variant="outline"
              size="icon"
              className="size-8 text-emerald-600 hover:text-emerald-500 dark:text-emerald-400 dark:hover:text-emerald-300"
              onClick={() => onEdit(String(festival.id))}
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
              onClick={() => setOpenDeleteModal(true)}
            >
              <Trash />
            </Button>
          </div>
        );
      },
    },
  ];
};

export { useFestivalColumns };
