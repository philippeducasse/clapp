import React from "react";
import { Pencil, Plus } from "lucide-react";
import { Action } from "@/interfaces/Enums";
import { capitalize } from "lodash";
interface FormHeaderProps {
  action: string;
  entityName: string;
}
const FormHeader = ({ action, entityName }: FormHeaderProps) => {
  return (
    <div className="border-gray-200 border-b ">
      <div className="p-6">
        <div className="flex items-center">
          {action === Action.EDIT ? (
            <Pencil
              className="text-emerald-600 bg-emerald-100 p-2 rounded-md dark:bg-emerald-900 dark:text-emerald-400"
              size={48}
            />
          ) : (
            <Plus
              className="text-emerald-600 bg-emerald-100 p-2 rounded-md dark:bg-emerald-900 dark:text-emerald-400"
              size={48}
            />
          )}
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
