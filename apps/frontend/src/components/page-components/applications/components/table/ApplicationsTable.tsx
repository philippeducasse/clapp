"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Application } from "@/interfaces/entities/Application";
import { useApplicationColumns } from "../../helpers/useApplicationColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setApplications, deleteApplication } from "@/redux/slices/applicationSlice";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { EntityName } from "@/interfaces/Enums";
import { getApplicationFilters } from "../../helpers/getApplicationFilters";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { applicationApiService } from "@/api/applicationApiService";

interface ApplicationsTableProps {
  initialData: PaginatedResponse<Application>;
}

export const ApplicationsTable = ({ initialData }: ApplicationsTableProps) => {
  const dispatch = useDispatch();
  const [applicationData, setApplicationData] =
    useState<PaginatedResponse<Application>>(initialData);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteApplicationId, setDeleteApplicationId] = useState<number | null>(null);

  useEffect(() => {
    dispatch(setApplications(applicationData.results));
  }, [dispatch, applicationData.results]);

  const handleDeleteClick = useCallback((id: number) => {
    setDeleteApplicationId(id);
    setOpenDeleteModal(true);
  }, []);

  const onConfirmDelete = useCallback(async () => {
    if (deleteApplicationId === null) return;
    await applicationApiService.remove(deleteApplicationId);

    setApplicationData((prev) => ({
      ...prev,
      results: prev.results.filter((app) => app.id !== deleteApplicationId),
      count: prev.count - 1,
    }));

    dispatch(deleteApplication(deleteApplicationId));
    setDeleteApplicationId(null);
  }, [deleteApplicationId, dispatch]);

  const columns = useApplicationColumns({ onDeleteClick: handleDeleteClick });
  const filters = useMemo(() => getApplicationFilters(), []);
  return (
    <>
      <DeleteModal
        open={openDeleteModal}
        onOpenChange={setOpenDeleteModal}
        onConfirm={onConfirmDelete}
        itemName="application"
      />
      <DataTable
        columns={columns}
        data={applicationData.results}
        entityName={EntityName.APPLICATION}
        filters={filters}
        defaultSorting={[{ id: "createdAt", desc: true }]}
      />
    </>
  );
};
