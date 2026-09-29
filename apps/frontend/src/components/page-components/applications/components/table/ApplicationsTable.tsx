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
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

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

  const [seasons, setSeasons] = useState<string[]>([]);
  const [selectedSeason, setSelectedSeason] = useState<string | undefined>();

  useEffect(() => {
    if (initialData?.metadata?.availableSeasons) {
      const availableSeasons = initialData.metadata.availableSeasons as string[];
      setSeasons(availableSeasons);
      setSelectedSeason(availableSeasons[0]);
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

  const fetchApplications = useCallback(
    (params: Parameters<typeof applicationApiService.getAll>[0]) =>
      applicationApiService.getAll({
        ...params,
        filters: { ...params?.filters, season: selectedSeason },
      }),
    [selectedSeason],
  );

  return (
    <>
      <DeleteModal
        open={openDeleteModal}
        onOpenChange={setOpenDeleteModal}
        onConfirm={onConfirmDelete}
        itemName="application"
      />

      {seasons && (
        <div className="inline-flex h-9 items-center justify-center rounded-lg bg-muted p-1 text-muted-foreground mb-4">
          {seasons.map((season) => (
            <Button
              key={season}
              type="button"
              variant="ghost"
              onClick={() => setSelectedSeason(season)}
              className={cn(
                "inline-flex h-auto items-center justify-center whitespace-nowrap rounded-md px-3 py-1 text-sm font-medium shadow-none ring-offset-background transition-all hover:bg-transparent hover:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
                selectedSeason === season &&
                  "bg-background text-foreground shadow hover:bg-background hover:text-foreground",
              )}
            >
              {season}
            </Button>
          ))}
        </div>
      )}
      <DataTable
        columns={columns}
        data={applicationData.results}
        entityName={EntityName.APPLICATION}
        filters={filters}
        defaultSorting={[{ id: "createdAt", desc: true }]}
        totalCount={applicationData.count}
        fetchData={fetchApplications}
        onDataFetched={handleDataFetched}
      />
    </>
  );
};
