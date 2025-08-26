import React from "react";
import { Pencil, Send, Plus } from "lucide-react";
import { Action } from "@/interfaces/Enums";
import { capitalize } from "lodash";
interface FormHeaderProps {
  action: string;
  entityName: string;
}
const FormHeader = ({ action, entityName }: FormHeaderProps) => {
  const getActionIcon = (action: string) => {
    const iconProps = {
      className: "text-emerald-600 bg-emerald-100 p-2 rounded-md dark:bg-emerald-900 dark:text-emerald-400",
      size: 48 as const,
    };

    switch (action) {
      case Action.EDIT:
        return <Pencil {...iconProps} />;
      case Action.APPLY:
        return <Send {...iconProps} />;
      default:
        return <Plus {...iconProps} />;
    }
  };
  return (
    <div className="border-gray-200 border-b ">
      <div className="p-6">
        <div className="flex items-center">
          {getActionIcon(action)}
          <div className="ml-4">
            <h3 className="text-xl font-semibold">{capitalize(action)}</h3>
            <p className="text-gray-400">
              {action === Action.EDIT ? `Edit ${entityName} manually` : `Create a new ${entityName}`}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormHeader;
