"use client";
import { useEffect, useState } from "react";
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
  const [applicationData, setApplicationData] = useState<PaginatedResponse<Application>>(initialData);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteApplicationId, setDeleteApplicationId] = useState<number | null>(null);

  useEffect(() => {
    dispatch(setApplications(applicationData.results));
  }, [dispatch, applicationData.results]);

  const handleDeleteClick = (id: number) => {
    setDeleteApplicationId(id);
    setOpenDeleteModal(true);
  };

  const onConfirmDelete = async () => {
    if (deleteApplicationId === null) return;
    await applicationApiService.remove(deleteApplicationId);

    // Update local state by filtering out the deleted application
    setApplicationData(prev => ({
      ...prev,
      results: prev.results.filter(app => app.id !== deleteApplicationId),
      count: prev.count - 1
    }));

    // Also update Redux for consistency
    dispatch(deleteApplication(deleteApplicationId));
    setDeleteApplicationId(null);
  };

  return (
    <>
      <DeleteModal
        open={openDeleteModal}
        onOpenChange={setOpenDeleteModal}
        onConfirm={onConfirmDelete}
        itemName="application"
      />
      <DataTable
        columns={useApplicationColumns({ onDeleteClick: handleDeleteClick })}
        data={applicationData.results}
        entityName={EntityName.APPLICATION}
        filters={getApplicationFilters()}
        defaultSorting={[{ id: "createdAt", desc: true }]}
      />
    </>
  );
};
