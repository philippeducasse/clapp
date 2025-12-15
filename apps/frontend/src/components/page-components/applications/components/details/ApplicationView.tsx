"use client";
import { useEffect, useState } from "react";
import { Clipboard } from "lucide-react";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectApplication, updateApplication } from "@/redux/slices/applicationSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { getApplicationBasicInfo } from "../../helpers/getApplicationDetails";
import { Info } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import { refreshApplication } from "../../helpers/refreshApplication";
import { useDispatch } from "react-redux";
import DeleteButton from "@/components/common/buttons/DeleteButton";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { applicationApiService } from "@/api/applicationApiService";
import { useRouter } from "next/navigation";

const ApplicationView = () => {
  const params = useParams();
  const applicationId = Number(params.id);
  const dispatch = useDispatch();
  const router = useRouter();
  const [openDeleteDialog, setOpenDeleteDialog] = useState(false);
  const application = useSelector((state: RootState) => selectApplication(state, applicationId));

  useEffect(() => {
    if (!application) {
      refreshApplication(applicationId, dispatch);
    }
  }, [applicationId, application, dispatch]);

  const onConfirmDelete = async () => {
    await applicationApiService.remove(applicationId);
    router.push("/applications");
  };

  if (!application) {
    return <Skeleton />;
  }

  return (
    <DetailsViewWrapper href="/applications">
      <DeleteModal
        open={openDeleteDialog}
        onOpenChange={setOpenDeleteDialog}
        onConfirm={onConfirmDelete}
        itemName={"application"}
      />
      <DetailsViewHeader
        title={application.emailSubject ?? ""}
        icon={<Clipboard className="text-emerald-600 dark:text-emerald-400" size={32} />}
        entityId={application.id}
        statusApiMethod={applicationApiService.changeStatus}
        updateSlice={updateApplication}
        actionElements={
          <>
            <EditButton href={`/applications/${application.id}/edit`} />{" "}
            <DeleteButton
              variant={"outline"}
              className="text-red-500 border border-red-500 hover:text-red-400 hover:bg-background"
              onDelete={() => setOpenDeleteDialog(true)}
            />
          </>
        }
      />
      <DetailsViewSection
        title="Application information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getApplicationBasicInfo(application)}
        ribbonValue={application.status}
        ribbonType="status"
      />
    </DetailsViewWrapper>
  );
};

export default ApplicationView;
