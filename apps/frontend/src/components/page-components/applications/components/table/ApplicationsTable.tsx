"use client";
import { useEffect } from "react";
import { Application } from "@/interfaces/entities/Application";
import { useApplicationColumns } from "../../helpers/useApplicationColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setApplications } from "@/redux/slices/applicationSlice";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { EntityName } from "@/interfaces/Enums";

interface ApplicationsTableProps {
  initialData: PaginatedResponse<Application>;
}

export const ApplicationsTable = ({ initialData }: ApplicationsTableProps) => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setApplications(initialData.results));
  }, [dispatch, initialData]);

  // const onEdit = (id: string) => {
  //   router.push(`/applications/${id}/edit`);
  // };

  const columns = useApplicationColumns();
  // onEdit
  return (
    <DataTable columns={columns} data={initialData.results} entityName={EntityName.APPLICATION} />
  );
};
