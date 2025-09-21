"use client";

import React, { useEffect } from "react";
import { University } from "lucide-react";
import EditButton from "@/components/common/buttons/EditButton";
import { useSelector } from "react-redux";
import {
  selectResidency,
  setSelectedResidency,
} from "@/redux/slices/residencySlice";
import { RootState } from "@/redux/store";
import { useDispatch } from "react-redux";
import { getResidencyBasicInfo } from "../../helpers/getResidencyBasicInfo";
import { getResidencyDetails } from "../../helpers/getResidencyDetails";
import { useRouter } from "next/navigation";
import { Info, NotebookTabs } from "lucide-react";
import { refreshResidency } from "../../helpers/refreshResidency";
import { Skeleton } from "@/components/ui/skeleton";
import GenericButton from "@/components/common/buttons/GenericButton";
import DetailsViewHeader from "@/components/common/details-view/DetailsViewHeader";
import DetailsViewSection from "@/components/common/details-view/DetailsViewSection";
import DetailsViewWrapper from "@/components/common/details-view/DetailsViewWrapper";
import { useParams } from "next/navigation";

const ResidencyView = () => {
  const params = useParams();
  const dispatch = useDispatch();
  const residencyId = Number(params.id);
  const residency = useSelector((state: RootState) =>
    selectResidency(state, residencyId)
  );
  const router = useRouter();

  useEffect(() => {
    if (!residency) {
      refreshResidency(residencyId, dispatch);
    } else {
      dispatch(setSelectedResidency(residency));
    }
  }, [residencyId, residency, dispatch]);

  if (!residency) {
    return <Skeleton />;
  }

  const goToApplyPage = async () => {
    router.push(`/residencies/${residencyId}/apply`);
  };

  return (
    <DetailsViewWrapper href="/residencies">
      <DetailsViewHeader
        title={residency.residencyName}
        subtitle={`${residency.town && `${residency.town}`}, ${
          residency.country
        }`}
        icon={
          <University
            className="text-emerald-600 dark:text-emerald-400"
            size={32}
          />
        }
        actionElements={
          <>
            <GenericButton
              onClick={goToApplyPage}
              label={"Apply to residency"}
              isLoading={false}
            />
            <EditButton href={`/residencies/${residency.id}/edit`} />
          </>
        }
      />
      <DetailsViewSection
        title="Basic information"
        icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
        data={getResidencyBasicInfo(residency)}
      />
      <DetailsViewSection
        title="Residency details"
        icon={
          <NotebookTabs className="text-emerald-600 dark:text-emerald-400" />
        }
        data={getResidencyDetails(residency)}
      />
    </DetailsViewWrapper>
  );
};

export default ResidencyView;
