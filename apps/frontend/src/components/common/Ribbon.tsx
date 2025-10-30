import React from "react";
import { TagAction } from "@/interfaces/Enums";
import { Star, Eye, TriangleAlert, X, CircleQuestionMark, EyeOff } from "lucide-react";

interface RibbonProps {
  tag: string;
}

const TAG_CONFIG = {
  [TagAction.STAR]: { color: "bg-yellow-500", icon: Star },
  [TagAction.WATCH]: { color: "bg-blue-700", icon: Eye },
  [TagAction.WARNING]: { color: "bg-orange-700", icon: TriangleAlert },
  [TagAction.INACTIVE]: { color: "bg-gray-700", icon: X },
  [TagAction.IRRELEVANT]: { color: "bg-gray-700", icon: EyeOff },
  [TagAction.OTHER]: { color: "bg-purple-700", icon: CircleQuestionMark },
};

const Ribbon = ({ tag }: RibbonProps) => {
  const config = TAG_CONFIG[tag as TagAction];
  if (!config) return null;
  const Icon = config.icon;
  return (
    <div
      className={`absolute top-3 -right-10 ${config.color} text-white text-xs font-semibold py-2 px-14 transform rotate-45 shadow-md z-10 flex items-center justify-center`}
    >
      <Icon size={24} className="" />
    </div>
  );
};

export default Ribbon;
