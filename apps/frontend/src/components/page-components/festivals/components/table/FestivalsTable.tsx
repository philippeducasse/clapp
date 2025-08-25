"use client";
import { useEffect } from "react";
import { Festival } from "@/interfaces/Festival";
import { getFestivalColumns } from "../../helpers/getFestivalColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useRouter } from "next/navigation";
import { useDispatch } from "react-redux";
import { setFestivals } from "@/redux/slices/festivalSlice";

interface FestivalsTableProps {
  festivals: Festival[];
}

export const FestivalsTable = ({ festivals }: FestivalsTableProps) => {
  const router = useRouter();
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setFestivals(festivals));
  }, [dispatch, festivals]);

  const onEdit = (id: string) => {
    router.push(`/festivals/${id}/edit`);
  };

  const columns = getFestivalColumns(onEdit);
  return <DataTable columns={columns} data={festivals} />;
};
