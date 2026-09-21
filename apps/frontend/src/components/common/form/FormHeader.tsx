import React, { ReactNode } from "react";
import { Pencil, Send, Plus, Upload, Bug } from "lucide-react";
import { Action } from "@/interfaces/Enums";
import { EntityName } from "@/interfaces/Enums";
import { capitalizeFirst } from "@/utils/stringUtils";

interface FormHeaderProps {
  action: Action;
  entityName?: EntityName;
  additionalActions?: ReactNode;
}
const FormHeader = ({ action, entityName, additionalActions }: FormHeaderProps) => {
  const getActionIcon = (action: Action) => {
    const iconProps = {
      className: "text-primary bg-primary/20 p-2 rounded-md",
      size: 48 as const,
    };

    switch (action) {
      case Action.EDIT:
        return <Pencil {...iconProps} />;
      case Action.APPLY:
        return <Send {...iconProps} />;
      case Action.UPLOAD:
        return <Upload {...iconProps} />;
      case Action.REPORT_BUG:
        return <Bug {...iconProps} />;
      default:
        return <Plus {...iconProps} />;
    }
  };

  const getSubtitle = (action: Action) => {
    switch (action) {
      case Action.EDIT:
        return `Edit ${entityName?.toLowerCase()}`;
      case Action.UPLOAD:
        return "Upload your own organisations";
      case Action.REPORT_BUG:
        return "Help us fix issues and improve the platform";
      default:
        return `Create a new ${entityName?.toLowerCase()}`;
    }
  };

  return (
    <div className="border-gray-200 border-b ">
      <div className="p-6">
        <div className="flex items-center">
          {getActionIcon(action)}
          <div className="ml-4">
            <h3 className="text-xl">{capitalizeFirst(action)}</h3>
            <p className="text-gray-400">{getSubtitle(action)}</p>
          </div>
        </div>
      </div>
      {additionalActions && additionalActions}
    </div>
  );
};

export default FormHeader;
