import React from "react";
import { TagAction } from "@/interfaces/Enums";
import { ApplicationStatus } from "@/interfaces/entities/Application";
import {
  Star,
  Eye,
  TriangleAlert,
  X,
  CircleQuestionMark,
  EyeOff,
  Send,
  MessageCircle,
  CheckCircle,
  XCircle,
  Clock,
  Ban,
  FileText,
} from "lucide-react";

interface RibbonProps {
  ribbonType: "tag" | "status";
  ribbonValue: string;
}

const TAG_CONFIG = {
  [TagAction.STAR]: { color: "bg-yellow-500", icon: Star },
  [TagAction.WATCH]: { color: "bg-blue-700", icon: Eye },
  [TagAction.WARNING]: { color: "bg-orange-700", icon: TriangleAlert },
  [TagAction.INACTIVE]: { color: "bg-gray-700", icon: X },
  [TagAction.IRRELEVANT]: { color: "bg-gray-700", icon: EyeOff },
  [TagAction.OTHER]: { color: "bg-purple-700", icon: CircleQuestionMark },
};

const STATUS_CONFIG = {
  [ApplicationStatus.APPLIED]: { color: "bg-blue-600", icon: Send },
  [ApplicationStatus.IN_DISCUSSION]: { color: "bg-purple-600", icon: MessageCircle },
  [ApplicationStatus.ACCEPTED]: { color: "bg-green-600", icon: CheckCircle },
  [ApplicationStatus.REJECTED]: { color: "bg-red-600", icon: XCircle },
  [ApplicationStatus.IGNORED]: { color: "bg-gray-600", icon: EyeOff },
  [ApplicationStatus.POSTPONED]: { color: "bg-yellow-600", icon: Clock },
  [ApplicationStatus.CANCELLED]: { color: "bg-orange-600", icon: Ban },
  [ApplicationStatus.DRAFT]: { color: "bg-gray-500", icon: FileText },
  [ApplicationStatus.NOT_APPLIED]: { color: "bg-gray-400", icon: X },
  [ApplicationStatus.OTHER]: { color: "bg-purple-700", icon: CircleQuestionMark },
};

const Ribbon = ({ ribbonType, ribbonValue }: RibbonProps) => {
  const config =
    ribbonType === "tag"
      ? TAG_CONFIG[ribbonValue as TagAction]
      : STATUS_CONFIG[ribbonValue as ApplicationStatus];

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
