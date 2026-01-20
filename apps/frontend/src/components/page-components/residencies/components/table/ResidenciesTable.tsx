"use client";
import { useCallback, useMemo, useState } from "react";
import { useResidencyColumns } from "../../helpers/useResidencyColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { EntityName } from "@/interfaces/Enums";
import { AppDispatch } from "@/redux/store";
import { Residency } from "@/interfaces/entities/Residency";
import { setResidencies, deleteResidency } from "@/redux/slices/residencySlice";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { residencyApiService } from "@/api/residencyApiService";
import { getResidencyFilters } from "../../helpers/getResidencyFilters";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";

interface ResidenciesTableProps {
  initialData: PaginatedResponse<Residency>;
}

export const ResidenciesTable = ({ initialData }: ResidenciesTableProps) => {
  const dispatch = useDispatch<AppDispatch>();
  const [residencyData, setResidencyData] = useState<PaginatedResponse<Residency>>(initialData);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteResidencyId, setDeleteResidencyId] = useState<number | null>(null);

  const handleDeleteClick = useCallback((id: number) => {
    setDeleteResidencyId(id);
    setOpenDeleteModal(true);
  }, []);

  const onConfirmDelete = useCallback(async () => {
    if (deleteResidencyId === null) return;
    await residencyApiService.remove(deleteResidencyId);

    setResidencyData((prev) => ({
      ...prev,
      results: prev.results.filter((residency) => residency.id !== deleteResidencyId),
      count: prev.count - 1,
    }));

    dispatch(deleteResidency(deleteResidencyId));
    setDeleteResidencyId(null);
  }, [deleteResidencyId, dispatch]);

  const handleDataFetched = useCallback(
    (data: PaginatedResponse<Residency>) => {
      setResidencyData(data);
      dispatch(setResidencies(data.results));
    },
    [dispatch],
  );

  const columns = useResidencyColumns({ onDeleteClick: handleDeleteClick });

  const filters = useMemo(() => getResidencyFilters(), []);

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
        data={residencyData.results}
        entityName={EntityName.RESIDENCY}
        filters={filters}
        totalCount={residencyData.count}
        fetchData={residencyApiService.getAll}
        onDataFetched={handleDataFetched}
      />
    </>
  );
};
