"use client";
import { useEffect } from "react";
import { Festival } from "@/interfaces/Festival";
import { getFestivalColumns } from "../../helpers/getFestivalColumns";
import { DataTable } from "@/components/ui/data-table";
import { useRouter } from "next/navigation";
import { useDispatch } from "react-redux";
import { setFestivals } from "@/redux/slices/festivalSlice";

interface FestivalTableProps {
  festivals: Festival[];
}

export const FestivalTable = ({ festivals }: FestivalTableProps) => {
  const router = useRouter();
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setFestivals(festivals));
  }, [dispatch, festivals]);

  const onEdit = (id: string) => {
    router.push(`/festivals/${id}`);
  };

  const columns = getFestivalColumns(onEdit);
  return <DataTable columns={columns} data={festivals} />;
};
