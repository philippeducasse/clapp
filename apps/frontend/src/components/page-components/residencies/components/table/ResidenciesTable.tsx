"use client";
import { useEffect } from "react";
import { useResidencyColumns } from "../../helpers/useResidencyColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { EntityName } from "@/interfaces/Enums";
import { AppDispatch } from "@/redux/store";
import { Residency } from "@/interfaces/Residency";
import { setResidencies } from "@/redux/slices/residencySlice";

interface ResidenciesTableProps {
  residencies: Residency[];
}

export const ResidenciesTable = ({ residencies }: ResidenciesTableProps) => {
  const dispatch = useDispatch<AppDispatch>();

  useEffect(() => {
    dispatch(setResidencies(residencies));
  }, [dispatch]);

  const columns = useResidencyColumns();

  return (
    <DataTable
      columns={columns}
      data={residencies}
      entityName={EntityName.RESIDENCY}
    />
  );
};
