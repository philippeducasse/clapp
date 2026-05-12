"use client";
import { Festival } from "@/interfaces/entities/Festival";
import { getFestivalFormFields } from "../../helpers/form/getFestivalFormFields";
import { festivalApiService } from "@/api/festivalApiService";
import { useRouter, useParams } from "next/navigation";
import { useDispatch, useSelector } from "react-redux";
import { updateFestival, selectFestival, setFestival } from "@/redux/slices/festivalSlice";
import { AppDispatch, RootState } from "@/redux/store";
import { refreshFestival } from "../../helpers/refreshFestival";
import FormHeader from "@/components/common/form/FormHeader";
import BasicForm from "@/components/common/form/BasicForm";
import { Action } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
import { useEntityForm } from "@/hooks/useEntityForm";

interface FestivalBasicInfoFormProps {
  action: Action;
}

const FestivalBasicInfoForm = ({ action }: FestivalBasicInfoFormProps) => {
  const dispatch: AppDispatch = useDispatch();
  const router = useRouter();
  const params = useParams();
  const festivalId = Number(params?.id);
  const festival = useSelector((state: RootState) => selectFestival(state, festivalId || -1));
  const formFields = getFestivalFormFields();
  const { form, isLoading, setIsLoading } = useEntityForm(
    festival,
    festivalId,
    formFields,
    refreshFestival,
    dispatch
  );

  const onSubmit = async (values: Record<string, unknown>) => {
    setIsLoading(true);
    try {
      if (action === Action.EDIT) {
        const updatedFestival = { ...values, id: festivalId } as Festival;
        await festivalApiService.update(updatedFestival);
        dispatch(updateFestival(updatedFestival));
        router.push(`/festivals/${festival?.id}`);
      } else {
        const tempFestival = { ...values, id: -1 };
        dispatch(setFestival(tempFestival as Festival));
        router.push(`/festivals/create/contact`);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const onCancelHref = festivalId ? `/festivals/${festival?.id}` : "/festivals";

  return (
    <>
      <FormHeader action={action} entityName={EntityName.FESTIVAL} />
      <BasicForm
        form={form}
        formFields={formFields}
        onSubmit={onSubmit}
        onCancelHref={onCancelHref}
        isLoading={isLoading}
        entity={festival}
        action={action}
        formTitle="Basic Information"
        submitButtonLabel={action === Action.CREATE ? "Next" : "Save"}
        formSubtitle={
          action === Action.CREATE
            ? "Please provide basic festival information. You will provide contact information next."
            : ""
        }
      />
    </>
  );
};
export default FestivalBasicInfoForm;
