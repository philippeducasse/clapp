"use client";
import { Residency } from "@/interfaces/entities/Residency";
import { getResidencyFormFields } from "../../helpers/form/getResidencyFormFields";
import { residencyApiService } from "@/api/residencyApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateResidency, selectResidency, setResidency } from "@/redux/slices/residencySlice";
import { AppDispatch, RootState } from "@/redux/store";
import { refreshResidency } from "../../helpers/refreshResidency";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action, EntityName } from "@/interfaces/Enums";
import { useEntityForm } from "@/hooks/useEntityForm";
interface ResidencyFormProps {
  action: Action;
}

const ResidencyBasicInfoForm = ({ action }: ResidencyFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const residencyId = Number(params?.id);
  const residency = useSelector((state: RootState) => selectResidency(state, residencyId || -1));
  const formFields = getResidencyFormFields();
  const { form, isLoading, setIsLoading } = useEntityForm(residency, residencyId, formFields, refreshResidency, dispatch);

  const onSubmit = async (values: Record<string, unknown>) => {
    setIsLoading(true);
    try {
      if (action === Action.EDIT) {
        const updatedResidency = { ...values, id: residencyId } as Residency;
        await residencyApiService.update(updatedResidency);
        dispatch(updateResidency(updatedResidency));
        router.push(`/residencies/${residency?.id}`);
      } else {
        const tempResidency = { ...values, id: -1 };
        dispatch(setResidency(tempResidency as Residency));
        router.push(`/residencies/create/contact`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const onCancelHref = residencyId ? `/residencies/${residency?.id}` : "/residencies";

  return (
    <>
      <FormHeader action={action} entityName={EntityName.RESIDENCY} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={residency}
        action={action}
        formTitle="Basic Information"
        submitButtonLabel={action === Action.CREATE ? "Next" : "Save"}
        formSubtitle={
          action === Action.CREATE
            ? "Please provide basic residency information. You will provide contact information next."
            : ""
        }
      />
    </>
  );
};
export default ResidencyBasicInfoForm;
