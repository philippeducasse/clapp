"use client";
import { useEffect, useState } from "react";
import { Application } from "@/interfaces/entities/Application";
import { useApplicationColumns } from "../helpers/useApplicationColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useRouter } from "next/navigation";
import { useDispatch } from "react-redux";
import { setApplications } from "@/redux/slices/applicationSlice";
import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { EntityName } from "@/interfaces/Enums";

interface ApplicationsTableProps {
  initialData: PaginatedResponse<Application>;
}

export const ApplicationsTable = ({ initialData }: ApplicationsTableProps) => {
  const router = useRouter();
  const dispatch = useDispatch();
  const [applicationData, setApplicationData] =
    useState<PaginatedResponse<Application>>(initialData);

  useEffect(() => {
    dispatch(setApplications(initialData.results));
  }, [dispatch, initialData]);

  const onEdit = (id: string) => {
    router.push(`/applications/${id}/edit`);
  };

  const columns =
    useApplicationColumns();
    // onEdit
  return (
    <DataTable
      columns={columns}
      data={applicationData.results}
      entityName={EntityName.APPLICATION}
    />
  );
};
