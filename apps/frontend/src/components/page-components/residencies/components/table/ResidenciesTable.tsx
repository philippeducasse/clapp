"use client";
import { useEffect, useState } from "react";
import { useResidencyColumns } from "../../helpers/useResidencyColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { EntityName } from "@/interfaces/Enums";
import { AppDispatch } from "@/redux/store";
import { Residency } from "@/interfaces/entities/Residency";
import { setResidencies, deleteResidency } from "@/redux/slices/residencySlice";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { residencyApiService } from "@/api/residencyApiService";

interface ResidenciesTableProps {
  residencies: Residency[];
}

export const ResidenciesTable = ({ residencies }: ResidenciesTableProps) => {
  const dispatch = useDispatch<AppDispatch>();
  const [residencyData, setResidencyData] = useState<Residency[]>(residencies);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteResidencyId, setDeleteResidencyId] = useState<number | null>(null);

  useEffect(() => {
    dispatch(setResidencies(residencyData));
  }, [dispatch, residencyData]);

  const handleDeleteClick = (id: number) => {
    setDeleteResidencyId(id);
    setOpenDeleteModal(true);
  };

  const onConfirmDelete = async () => {
    if (deleteResidencyId === null) return;
    await residencyApiService.remove(deleteResidencyId);

    // Update local state by filtering out the deleted residency
    setResidencyData(prev => prev.filter(residency => residency.id !== deleteResidencyId));

    // Also update Redux for consistency
    dispatch(deleteResidency(deleteResidencyId));
    setDeleteResidencyId(null);
  };

  const columns = useResidencyColumns({ onDeleteClick: handleDeleteClick });

  return (
    <>
      <DeleteModal
        open={openDeleteModal}
        onOpenChange={setOpenDeleteModal}
        onConfirm={onConfirmDelete}
        itemName="residency"
      />
      <DataTable
        columns={columns}
        data={residencyData}
        entityName={EntityName.RESIDENCY}
      />
    </>
  );
};
