import React from "react";
import { Pencil } from "lucide-react";
interface FormHeaderProps {
  title?: string;
  subtitle?: string;
}
const FormHeader = ({ title, subtitle }: FormHeaderProps) => {
  return (
    <div className="border-gray-200 border-b ">
      <div className="p-6">
        <div className="flex items-center">
          <Pencil className="text-emerald-600 bg-emerald-100 p-2 rounded-md" size={48} />
          <div className="ml-4">
            <h3 className="text-xl font-semibold">{title ?? "Edit"}</h3>
            <p className="text-gray-400">{subtitle ?? "Edit festival entries manually."} </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormHeader;
