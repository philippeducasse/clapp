import { Residency } from "@/interfaces/Residency";
import { getControlledFormFields } from "@/helpers/formHelper";

export const getResidencyFormFields = (residency?: Residency) => {
  const fields = {
    name: {
      label: "Name",
      value: residency?.name,
    },
    description: {
      label: "Description",
      value: residency?.description,
      type: "textarea",
    },
    location: {
      label: "Location",
      value: residency?.location,
    },
    startDate: {
      label: "Start Date",
      value: residency?.startDate,
      type: "date",
    },
    endDate: {
      label: "End Date",
      value: residency?.endDate,
      type: "date",
    },
    website: {
      label: "Website",
      value: residency?.website,
    },
    imageUrl: {
      label: "Image URL",
      value: residency?.imageUrl,
    },
  };

  return getControlledFormFields(fields);
};
