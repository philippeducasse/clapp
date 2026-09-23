"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Application,
  ApplicationStatus,
} from "@/interfaces/entities/Application";
import { useApplicationColumns } from "../../helpers/useApplicationColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch, useSelector } from "react-redux";
import {
  setApplications,
  deleteApplication,
  updateApplication,
} from "@/redux/slices/applicationSlice";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { EntityName } from "@/interfaces/Enums";
import { getApplicationFilters } from "../../helpers/getApplicationFilters";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { applicationApiService } from "@/api/applicationApiService";
import DetailsTabs, { Tab } from "@/components/common/details-view/DetailsTabs";
import { useHashTab } from "@/hooks/useHashTab";

interface ApplicationsTableProps {
  initialData: PaginatedResponse<Application>;
}

export const ApplicationsTable = ({ initialData }: ApplicationsTableProps) => {
  const dispatch = useDispatch();

  const [applicationData, setApplicationData] =
    useState<PaginatedResponse<Application>>(initialData);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteApplicationId, setDeleteApplicationId] = useState<number | null>(
    null,
  );

  const [seasons, setSeasons] = useState<number[]>([]);
  const { activeTab, handleTabChange } = useHashTab(String(seasons[0]) ?? null);

  useEffect(() => {
    if (initialData?.metadata?.availableYears) {
      setSeasons(initialData.metadata.availableYears as number[]);
    }
  }, [initialData]);

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

  const handleStatusChange = useCallback(
    async (id: number, status: ApplicationStatus) => {
      const updatedApplication = await applicationApiService.changeStatus(
        id,
        status,
      );

      setApplicationData((prev) => ({
        ...prev,
        results: prev.results.map((app) =>
          app.id === id ? updatedApplication : app,
        ),
      }));

      dispatch(updateApplication(updatedApplication));
    },
    [dispatch],
  );

  const handleDataFetched = useCallback(
    (data: PaginatedResponse<Application>) => {
      setApplicationData(data);
      dispatch(setApplications(data.results));
    },
    [dispatch],
  );

  const columns = useApplicationColumns({
    onDeleteClick: handleDeleteClick,
    onStatusChange: handleStatusChange,
  });
  const filters = useMemo(() => getApplicationFilters(), []);
  return (
    <>
      <DeleteModal
        open={openDeleteModal}
        onOpenChange={setOpenDeleteModal}
        onConfirm={onConfirmDelete}
        itemName="application"
      />

      {seasons && (
        <DetailsTabs defaultTab={activeTab} onTabChange={handleTabChange}>
          {seasons.map((season) => (
            <Tab name={String(season)}>
              <></>
            </Tab>
          ))}
        </DetailsTabs>
      )}
      <DataTable
        columns={columns}
        data={applicationData.results}
        entityName={EntityName.APPLICATION}
        filters={filters}
        defaultSorting={[{ id: "createdAt", desc: true }]}
        totalCount={applicationData.count}
        fetchData={applicationApiService.getAll}
        onDataFetched={handleDataFetched}
      />
    </>
  );
};
