"use client";
import { useEffect } from "react";
import { Clipboard } from "lucide-react";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import { selectApplication } from "@/redux/slices/applicationSlice";
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

const ApplicationView = () => {
  const params = useParams();
  const applicationId = Number(params.id);
  const dispatch = useDispatch();

  const application = useSelector((state: RootState) => selectApplication(state, applicationId));

  useEffect(() => {
    if (!application) {
      refreshApplication(applicationId, dispatch);
    }
  }, [applicationId, application, dispatch]);

  if (!application) {
    return <Skeleton />;
  }

  return (
    <DetailsViewWrapper href="/applications">
      <DetailsViewHeader
        title={application.emailSubject ?? ""}
        icon={<Clipboard className="text-emerald-600 dark:text-emerald-400" size={32} />}
        actionElements={<EditButton href={`/applications/${application.id}/edit`} />}
      />
      <DetailsViewSection
        title="Application information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getApplicationBasicInfo(application)}
      />
    </DetailsViewWrapper>
  );
};

export default ApplicationView;
