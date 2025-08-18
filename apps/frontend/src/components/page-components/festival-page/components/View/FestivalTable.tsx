"use client";

import { Festival } from "@/interfaces/Festival";
import { getFestivalColumns } from "../../helpers/getFestivalColumns";
import { DataTable } from "@/components/ui/data-table";
import { useRouter } from "next/navigation";

interface FestivalTableProps {
  data: Festival[];
}

export const FestivalTable = ({ data }: FestivalTableProps) => {
  const router = useRouter();

  const onEdit = (id: string) => {
    router.push(`/festivals/${id}`);
  };

  const columns = getFestivalColumns(onEdit);
  return <DataTable columns={columns} data={data} />;
};
