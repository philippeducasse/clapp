"use client";
import { useEffect } from "react";
import { Festival } from "@/interfaces/Festival";
import { useFestivalColumns } from "../../helpers/useFestivalColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setFestivals } from "@/redux/slices/festivalSlice";
import { EntityName } from "@/interfaces/Enums";

interface FestivalsTableProps {
  festivals: Festival[];
}

export const FestivalsTable = ({ festivals }: FestivalsTableProps) => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setFestivals(festivals));
  }, [dispatch, festivals]);

  const columns = useFestivalColumns();

  return <DataTable columns={columns} data={festivals} entityName={EntityName.FESTIVAL} />;
};
