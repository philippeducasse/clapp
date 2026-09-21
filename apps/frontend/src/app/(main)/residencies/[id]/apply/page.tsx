import ApplicationForm from "@/components/page-components/applications/components/form/ApplicationForm";
import { EntityName } from "@/interfaces/Enums";

const ResidencyApplicationPage = () => {
  return <ApplicationForm entityName={EntityName.RESIDENCY} />;
};

export default ResidencyApplicationPage;
